from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages  # optional, for error messages
from apps.users.models import CustomUser, ForgotPasswordOTP
from django.views import View
from apps.users.forms import CustomUserSignupForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta, timezone
import logging
from urllib.parse import quote_plus
from django.utils.crypto import get_random_string

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timesince import timesince
from django.core.mail import EmailMultiAlternatives
import json, traceback,random
from .models import ForgotPasswordOTP
from apps.stats.core import compute_all_metrics, compute_complain
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import Permission



logger = logging.getLogger(__name__)
User = get_user_model()
otp_storage = {}

class StatisticsView(View):
    def get(self, request):

        # If user is not logged in → send to login
        if not request.user.is_authenticated:
            return render(request, "auth/login.html")

        user = request.user

        # If user is not CUSTOMER → show full stats
        if user.role != "CUSTOMER":
            full_data = compute_all_metrics(user)
            return render(request, "dashboard.html", {"full_data": full_data})

        # If user is CUSTOMER → show limited stats
        user_data = compute_complain(user)
        return render(request, "dashboard.html", {"user_data": user_data})


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user-details')
        return render(request, "auth/login.html")
    
    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        print(user)

        if user is not None:
            login(request, user)
            return redirect("user-details")
        else:
            messages.error(request, "Invalid email or password")
            return render(request, "auth/login.html", {"email": email})
    
def logout_view(request):
    logout(request)  # Clears the session and logs out the user
    return redirect('login')


def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"success": False, "error": "Email is required."})

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({"success": False, "error": "Email not found."})

            otp = random.randint(100000, 999999)

            from .models import ForgotPasswordOTP
            ForgotPasswordOTP.objects.update_or_create(
                email=email,
                defaults={
                    "otp": otp,
                    "created_at": timezone.now()
                }
            )

            context = {
                "user": user.get_full_name() or user.username,
                "otp_code": otp,
                "validity": 10
            }

            subject = "Your Password Reset OTP"
            html_content = render_to_string("auth/otp_email.html", context)
            text_content = f"Your OTP for password reset is {otp}. It will expire in 10 minutes."

            try:
                email_message = EmailMultiAlternatives(
                    subject,
                    text_content,
                    "asr@johnnette.com",
                    [email]
                )
                email_message.attach_alternative(html_content, "text/html")
                email_message.send(fail_silently=False)
                print("✅ OTP email sent successfully!")
            except Exception as e:
                print("❌ Email sending failed:", e)
                traceback.print_exc()
                return JsonResponse({"success": False, "error": f"Email sending failed: {str(e)}"})

            return JsonResponse({"success": True})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')

        # print("DEBUG DATA:", email, otp, new_password)

        # check required fields
        if not all([email, otp, new_password]):
            return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

        # find OTP record
        otp_entry = ForgotPasswordOTP.objects.filter(email=email, otp=otp).first()
        # print("DEBUG OTP ENTRY:", otp_entry)

        if not otp_entry:
            return JsonResponse({'success': False, 'error': 'Invalid OTP'}, status=400)

        # check expiry (10 minutes)
        expiry_time = otp_entry.created_at + timedelta(minutes=10)
        # print("DEBUG Expiry:", expiry_time, "Now:", timezone.now())

        if timezone.now() > expiry_time:
            otp_entry.delete()
            return JsonResponse({'success': False, 'error': 'OTP expired. Please request a new one.'}, status=400)

        # find user
        user = User.objects.filter(email=email).first()
        # print("DEBUG USER:", user)

        if not user:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

        # update password
        user.set_password(new_password)
        user.save()
        otp_entry.delete()  # clear OTP once used

        print("✅ Password reset successful for", email)
        # return JsonResponse({'success': True})

    except Exception as e:
        # print("❌ Error in verify_otp:", e)
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# class SignupView(CreateView):
#     model = CustomUser
#     form_class = CustomUserSignupForm
#     template_name = "auth/signup.html"
#     success_url = reverse_lazy("login")  # redirect after successful signup

#     def form_valid(self, form):
#         user = form.save()
#         messages.success(self.request, "✅ Account created successfully. Please log in.")
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "⚠️ There was an error creating your account. Please check the form.")
#         return super().form_invalid(form)

from django.views.generic import CreateView

class SignupView(CreateView):
    model = CustomUser
    form_class = CustomUserSignupForm
    template_name = "auth/signup.html"
    success_url = reverse_lazy("login")

    def get_form_kwargs(self):
        """
        Inject the request into the form so that
        the form can access session (OTP verification).
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """
        This is called ONLY if:
        - all form fields are valid
        - password validators pass
        - OTP validation in form.clean() passes
        """
        response = super().form_valid(form)

        # Cleanup OTP session after successful signup
        self.request.session.pop("email_verified", None)
        self.request.session.pop("email_otp", None)

        messages.success(
            self.request,
            "✅ Account created successfully. Please log in."
        )
        return response

    def form_invalid(self, form):
        """
        Explicitly render the same page with form errors.
        (CreateView already does this, but we keep it explicit
        for clarity and debugging.)
        """
        return self.render_to_response(
            self.get_context_data(form=form)
        )



import random
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.conf import settings


@require_POST
def send_email_otp(request):
    email = request.POST.get("email")

    otp = str(random.randint(100000, 999999))

    request.session["email_otp"] = otp
    request.session["email_verified"] = False
    request.session.modified = True

    print("OTP SENT:", otp)

    send_mail(
        "Email Verification JASS",
        f"Your OTP is {otp}. It is valid for 5 minutes. For security reasons, do not share this OTP with anyone.",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    return JsonResponse({"success": True})



@require_POST
def verify_email_otp(request):
    entered_otp = request.POST.get("otp", "").strip()
    session_otp = request.session.get("email_otp")

    print("ENTERED OTP:", entered_otp)
    print("SESSION OTP:", session_otp)

    if not session_otp:
        return JsonResponse({
            "success": False,
            "message": "OTP expired. Please resend OTP."
        })

    if entered_otp == session_otp:
        request.session["email_verified"] = True
        request.session.modified = True
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid OTP"})


    
class UserDetails(LoginRequiredMixin,View):
    login_url = 'login'
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, "dashboard.html", {"user": None})

class UserManagementListView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    """View for displaying and managing user lists with filtering and pagination."""
    
    login_url = 'login'
    permission_required = "users.view_customuser"
    template_name = "users/user_management.html"

    def get_context_data(self, **kwargs):
        """Builds context data for user management template by coordinating specialized processors."""
        context = super().get_context_data(**kwargs)
        request = self.request

        # Process data through specialized components
        filter_processor = UserFilterProcessor(request)
        filtered_users = filter_processor.get_filtered_queryset()
        
        pagination_processor = UserPaginationProcessor(filtered_users, request)
        page_obj = pagination_processor.get_page_obj()
        
        data_processor = UserDataProcessor(page_obj)
        user_rows = data_processor.get_user_rows()

        context.update({
            "user_rows": user_rows,
            "page_obj": page_obj,
            "page_range": pagination_processor.get_elided_page_range(),
            "stats": filter_processor.get_statistics(),
            "current_filters": filter_processor.get_current_filters(),
            "role_choices": CustomUser.ROLE_CHOICES,
            "sort_options": self.get_sort_options(),
            "query_string": filter_processor.get_query_string(),
        })
        return context

    def get_sort_options(self):
        """Returns available sorting options for the user list."""
        return [
            ("-date_joined", "Newest first"),
            ("first_name", "Alphabetical"),
            ("-last_login", "Last active"),
        ]

class UserFilterProcessor:
    """Handles filtering, searching, and sorting of user querysets."""
    
    def __init__(self, request):
        """Initializes with request and extracts filter parameters."""
        self.request = request
        self.search_query = request.GET.get("q", "").strip()
        self.role_filter = request.GET.get("role", "").strip()
        self.status_filter = request.GET.get("status", "").strip()
        self.sort_by = request.GET.get("sort", "-date_joined")
        self.base_queryset = CustomUser.objects.all()

    def get_filtered_queryset(self):
        """Applies all filters and returns the final queryset."""
        queryset = self.base_queryset
        
        if self.search_query:
            queryset = self._apply_search_filter(queryset)
        
        if self.role_filter:
            queryset = queryset.filter(role=self.role_filter)
        
        if self.status_filter:
            queryset = self._apply_status_filter(queryset)
        
        return self._apply_sorting(queryset)

    def _apply_search_filter(self, queryset):
        """Filters queryset based on search query across multiple fields."""
        return queryset.filter(
            Q(first_name__icontains=self.search_query)
            | Q(last_name__icontains=self.search_query)
            | Q(email__icontains=self.search_query)
            | Q(certificate_number__icontains=self.search_query)
        )

    def _apply_status_filter(self, queryset):
        """Filters queryset based on user status (active/inactive/invited)."""
        if self.status_filter == "active":
            return queryset.filter(is_active=True, last_login__isnull=False)
        elif self.status_filter == "inactive":
            return queryset.filter(is_active=False)
        elif self.status_filter == "invited":
            return queryset.filter(is_active=True, last_login__isnull=True)
        return queryset

    def _apply_sorting(self, queryset):
        """Applies sorting to the queryset based on selected option."""
        sort_mapping = {
            "-date_joined": "-date_joined",
            "first_name": "first_name",
            "-last_login": "-last_login",
        }
        return queryset.order_by(sort_mapping.get(self.sort_by, "-date_joined"))

    def get_statistics(self):
        """Returns counts for different user status categories."""
        queryset = self.get_filtered_queryset()
        return {
            "total": queryset.count(),
            "active": queryset.filter(is_active=True, last_login__isnull=False).count(),
            "inactive": queryset.filter(is_active=False).count(),
            "pending": queryset.filter(is_active=True, last_login__isnull=True).count(),
        }

    def get_current_filters(self):
        """Returns current filter values for template rendering."""
        return {
            "q": self.search_query,
            "role": self.role_filter,
            "status": self.status_filter,
            "sort": self.sort_by,
        }

    def get_query_string(self):
        """Returns query string for pagination links while preserving filters."""
        preserved_query = self.request.GET.copy()
        preserved_query.pop("page", None)
        return preserved_query.urlencode()
class UserPaginationProcessor:
    """Handles pagination logic for user lists."""
    
    def __init__(self, queryset, request, per_page=10):
        """Initializes paginator with queryset and request parameters."""
        self.queryset = queryset
        self.request = request
        self.per_page = per_page
        self.paginator = Paginator(queryset, per_page)
        self.page_obj = self._get_page_obj()

    def _get_page_obj(self):
        """Returns the current page object based on request."""
        page_number = self.request.GET.get("page")
        return self.paginator.get_page(page_number)

    def get_page_obj(self):
        """Returns the current page object."""
        return self.page_obj

    def get_elided_page_range(self, on_each_side=1, on_ends=1):
        """Returns elided page range for pagination controls."""
        return self.paginator.get_elided_page_range(
            self.page_obj.number, 
            on_each_side=on_each_side, 
            on_ends=on_ends
        )

class UserDataProcessor:
    """Processes user objects into template-ready dictionary data."""
    
    def __init__(self, page_obj):
        """Initializes with a page object containing users."""
        self.page_obj = page_obj

    def get_user_rows(self):
        """Processes all users in page object into template data."""
        return [self._process_user_data(user) for user in self.page_obj]

    def _process_user_data(self, user):
        """Converts a single user object into template data dictionary."""
        full_name = self._get_user_full_name(user)
        status_data = self._get_status_data(user)
        
        return {
            "id": user.id,
            "full_name": full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "certificate_number": user.certificate_number or "",
            "designation": user.designation or "",
            "avatar_url": self._get_avatar_url(full_name, user.email),
            "role": user.role,
            "role_display": user.get_role_display(),
            "command_name": user.command_name or "",
            "is_active": user.is_active,
            "access_tags": self._get_access_tags(user),
            "last_login_display": self._get_last_login_display(user),
            "status_indicator": status_data["indicator"],
            "status_label": status_data["label"],
            "status_text_class": status_data["text_class"],
            "status_subtitle": status_data["subtitle"],
        }

    def _get_user_full_name(self, user):
        """Returns user's full name or falls back to email username."""
        full_name = (user.get_full_name() or "").strip()
        return full_name or user.email.split("@")[0]

    def _get_avatar_url(self, full_name, email):
        """Generates avatar URL based on user's name or email."""
        avatar_seed = quote_plus(full_name or email)
        return f"https://ui-avatars.com/api/?name={avatar_seed}&background=random"

    def _get_last_login_display(self, user):
        """Formats last login time for display."""
        if user.last_login:
            return f"{timesince(user.last_login)} ago"
        return "Never logged in"

    def _get_status_data(self, user):
        """Determines user status data for display and styling."""
        if not user.is_active:
            return {
                "label": "Inactive",
                "indicator": "status-inactive",
                "text_class": "text-danger",
                "subtitle": "Account disabled"
            }
        elif user.last_login:
            return {
                "label": "Active",
                "indicator": "status-active",
                "text_class": "text-success",
                "subtitle": f"Last login {self._get_last_login_display(user)}"
            }
        else:
            return {
                "label": "Invite Pending",
                "indicator": "status-pending",
                "text_class": "text-warning",
                "subtitle": "Awaiting first login"
            }

    def _get_access_tags(self, user):
        """Compiles list of access tags from groups and permissions."""
        access_tags = list(user.groups.values_list("name", flat=True))
        
        if len(access_tags) < 4:
            access_tags = self._add_extra_permissions(user, access_tags)
        
        if not access_tags:
            access_tags.append(user.get_role_display())
            
        return access_tags

    def _add_extra_permissions(self, user, access_tags):
        """Adds individual permissions as tags when group tags are insufficient."""
        extra_perms = user.user_permissions.values_list("codename", flat=True)
        for perm in extra_perms:
            if len(access_tags) >= 4:
                break
            humanised = perm.replace("_", " ").title()
            if humanised not in access_tags:
                access_tags.append(humanised)
        return access_tags
class CreateOEMUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = 'login'
    permission_required = "users.add_customuser"
    template_name = "users/create_oem_user_form.html"
    
    def get(self, request):
        context = {
            'role_choices': CustomUser.ROLE_CHOICES,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        try:
            # Create user
            user = CustomUser.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email').lower(),
                phone_number=request.POST.get('phone_number'),
                certificate_number=request.POST.get('certificate_number') or None,
                designation=request.POST.get('designation') or None,
                command_name=request.POST.get('command_name') or None,
                role=request.POST.get('role'),
                is_active=request.POST.get('is_active') == 'on',
            )
            
            # Set password
            password1 = request.POST.get('password1')
            if password1:
                user.set_password(password1)
            else:
                # Auto-generate password
                password = get_random_string(12)
                user.set_password(password)
            user.save()
            
            # Send invite if requested
            send_invite = request.POST.get('send_invite') == 'on'
            if send_invite:
                # TODO: Send invitation email with password reset link
                messages.success(request, f"User {user.get_full_name()} created successfully. Invitation email sent.")
            else:
                messages.success(request, f"User {user.get_full_name()} created successfully.")
            
            return redirect('user_list')
        
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            context = {
                'role_choices': CustomUser.ROLE_CHOICES,
            }
            # return redirect('user_list')
            return render(request, self.template_name, context)


class EditOEMUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = 'login'
    permission_required = "users.change_customuser"
    template_name = "users/create_oem_user_form.html"
    
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        context = {
            'user': user,
            'role_choices': CustomUser.ROLE_CHOICES,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        try:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email').lower()
            user.phone_number = request.POST.get('phone_number')
            user.certificate_number = request.POST.get('certificate_number') or None
            user.designation = request.POST.get('designation') or None
            user.command_name = request.POST.get('command_name') or None
            user.role = request.POST.get('role')
            user.is_active = request.POST.get('is_active') == 'on'
            
            # Update password if provided
            password1 = request.POST.get('password1')
            if password1:
                user.set_password(password1)
            
            user.save()
            messages.success(request, f"User {user.get_full_name()} updated successfully.")
            return redirect('user_list')
        except Exception as e:
            logger.error(f"Error updating user {pk}: {str(e)}", exc_info=True)
            messages.error(request, f"Error updating user: {str(e)}")
            return redirect('user_list')


class profileView(LoginRequiredMixin,View): 
    login_url = 'login'
    redirect_field_name = 'next'
    def get(self,request):
        context = {
            'user': request.user,
        }

        return render(request,'users/profile.html',context)
    
    def post(self, request):
            user = request.user
            user.first_name = request.POST.get("firstName")
            user.last_name = request.POST.get("lastName")
            user.email = request.POST.get("email")
            user.phone_number = request.POST.get("phone_number")  # must exist in your custom user model
            user.designation = request.POST.get("designation")
            user.command_name = request.POST.get("command_name")
            user.save()

            messages.success(request, "Profile updated successfully ✅")
            return redirect("profile")  # reload page with updated info



class UserPermissionManagementView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    """View for managing user permissions grouped by model."""
    
    login_url = 'login'
    permission_required = "users.change_customuser"
    template_name = "users/user_permission_management.html"
    
    def get_context_data(self, **kwargs):
        """Builds context data for permission management template."""
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        
        # Get the user being edited
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Get all permissions grouped by model
        permissions_by_model = self._get_permissions_grouped_by_model()
        
        # Get user's current permissions
        user_permissions = set(user.user_permissions.values_list('id', flat=True))
        
        context.update({
            "user": user,
            "permissions_by_model": permissions_by_model,
            "user_permissions": user_permissions,
        })
        return context
    
    def _get_permissions_grouped_by_model(self):
        """Fetches all permissions and groups them by model."""
        permissions = Permission.objects.all().select_related('content_type').order_by('content_type__app_label', 'content_type__model')
        
        grouped = {}
        for perm in permissions:
            model_name = perm.content_type.model
            app_label = perm.content_type.app_label
            
            # Skip Django admin and auth app permissions (except our custom ones)
            if app_label not in ['admin', 'sessions', 'contenttypes', 'authtoken']:
                key = f"{app_label}.{model_name}"
                
                if key not in grouped:
                    grouped[key] = {
                        "app_label": app_label,
                        "model_name": model_name,
                        "display_name": perm.content_type.model.replace('_', ' ').title(),
                        "permissions": []
                    }
                
                grouped[key]["permissions"].append({
                    "id": perm.id,
                    "name": perm.name,
                    "codename": perm.codename,
                })
        
        return grouped
    
    def post(self, request, user_id):
        """Updates user permissions based on POST data."""
        try:
            user = get_object_or_404(CustomUser, id=user_id)
            
            # Get permission IDs from request
            permission_ids = request.POST.getlist('permissions[]')
            permission_ids = [int(pid) for pid in permission_ids if pid.isdigit()]
            
            # Update user permissions
            user.user_permissions.set(permission_ids)
            
            messages.success(request, f"Permissions for {user.first_name} {user.last_name} updated successfully!")
            return redirect('user_list')
        
        except Exception as e:
            messages.error(request, f"Error updating permissions: {str(e)}")
            logger.error(f"Permission update error: {str(e)}")
            return redirect('user_list')



# def custom_404_view(request, exception=None):
#     return render(request, "404.html", status=404)

# def custom_403_view(request, exception=None):
#     return render(request, "403.html", status=403)

# def custom_500_view(request):
#     return render(request, "500.html", status=500)