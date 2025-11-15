from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
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
from django.utils.timezone import now
from datetime import datetime, timedelta, timezone
import logging
import random
import json
from urllib.parse import quote_plus
from django.utils.crypto import get_random_string

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timesince import timesince


logger = logging.getLogger(__name__)
User = get_user_model()


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



otp_storage = {}




from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json, random
from datetime import timedelta
import traceback

User = get_user_model()

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




from django.http import JsonResponse
from django.utils import timezone
import json, traceback
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import ForgotPasswordOTP

User = get_user_model()

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


class SignupView(CreateView):
    model = CustomUser
    form_class = CustomUserSignupForm
    template_name = "auth/signup.html"
    success_url = reverse_lazy("login")  # redirect after successful signup

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "✅ Account created successfully. Please log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "⚠️ There was an error creating your account. Please check the form.")
        return super().form_invalid(form)
    
    
class UserDetails(LoginRequiredMixin,View):
    login_url = 'login'
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, "dashboard.html", {"user": None})


class UserManagementListView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    login_url = 'login'
    permission_required = "auth.view_user"
    template_name = "users/user_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        users_qs = CustomUser.objects.all()

        search_query = request.GET.get("q", "").strip()
        role_filter = request.GET.get("role", "").strip()
        status_filter = request.GET.get("status", "").strip()
        sort_by = request.GET.get("sort", "-date_joined")

        if search_query:
            users_qs = users_qs.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(certificate_number__icontains=search_query)
            )

        if role_filter:
            users_qs = users_qs.filter(role=role_filter)

        if status_filter == "active":
            users_qs = users_qs.filter(is_active=True, last_login__isnull=False)
        elif status_filter == "inactive":
            users_qs = users_qs.filter(is_active=False)
        elif status_filter == "invited":
            users_qs = users_qs.filter(is_active=True, last_login__isnull=True)

        sort_mapping = {
            "-date_joined": "-date_joined",
            "first_name": "first_name",
            "-last_login": "-last_login",
        }
        users_qs = users_qs.order_by(sort_mapping.get(sort_by, "-date_joined"))

        paginator = Paginator(users_qs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        elided_page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)

        user_rows = []
        for user in page_obj:
            full_name = (user.get_full_name() or "").strip()
            if not full_name:
                full_name = user.email.split("@")[0]

            avatar_seed = quote_plus(full_name or user.email)
            avatar_url = f"https://ui-avatars.com/api/?name={avatar_seed}&background=random"

            last_login_display = "Never logged in"
            if user.last_login:
                last_login_display = f"{timesince(user.last_login)} ago"

            if not user.is_active:
                status_label = "Inactive"
                status_indicator = "status-inactive"
                status_text_class = "text-danger"
                status_subtitle = "Account disabled"
            elif user.last_login:
                status_label = "Active"
                status_indicator = "status-active"
                status_text_class = "text-success"
                status_subtitle = f"Last login {last_login_display}"
            else:
                status_label = "Invite Pending"
                status_indicator = "status-pending"
                status_text_class = "text-warning"
                status_subtitle = "Awaiting first login"

            access_tags = list(user.groups.values_list("name", flat=True))
            if len(access_tags) < 4:
                extra_perms = user.user_permissions.values_list("codename", flat=True)
                for perm in extra_perms:
                    humanised = perm.replace("_", " ").title()
                    if humanised not in access_tags:
                        access_tags.append(humanised)
                    if len(access_tags) >= 4:
                        break
            if not access_tags:
                access_tags.append(user.get_role_display())

            user_rows.append(
                {
                    "id": user.id,
                    "full_name": full_name,
                    "email": user.email,
                    "avatar_url": avatar_url,
                    "role_display": user.get_role_display(),
                    "command_name": user.command_name or "",
                    "access_tags": access_tags,
                    "last_login_display": last_login_display,
                    "status_indicator": status_indicator,
                    "status_label": status_label,
                    "status_text_class": status_text_class,
                    "status_subtitle": status_subtitle,
                }
            )

        stats = {
            "total": users_qs.count(),
            "active": users_qs.filter(is_active=True, last_login__isnull=False).count(),
            "inactive": users_qs.filter(is_active=False).count(),
            "pending": users_qs.filter(is_active=True, last_login__isnull=True).count(),
        }

        preserved_query = request.GET.copy()
        preserved_query.pop("page", None)
        query_string = preserved_query.urlencode()

        context.update(
            {
                "user_rows": user_rows,
                "page_obj": page_obj,
                "page_range": elided_page_range,
                "stats": stats,
                "current_filters": {
                    "q": search_query,
                    "role": role_filter,
                    "status": status_filter,
                    "sort": sort_by,
                },
                "role_choices": CustomUser.ROLE_CHOICES,
                "sort_options": [
                    ("-date_joined", "Newest first"),
                    ("first_name", "Alphabetical"),
                    ("-last_login", "Last active"),
                ],
                "query_string": query_string,
            }
        )
        return context


class CreateOEMUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = 'login'
    permission_required = "auth.add_user"
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
            
            return redirect('user_admin_list')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            context = {
                'role_choices': CustomUser.ROLE_CHOICES,
            }
            return render(request, self.template_name, context)


class EditOEMUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = 'login'
    permission_required = "auth.change_user"
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
            return redirect('user_admin_list')
        except Exception as e:
            messages.error(request, f"Error updating user: {str(e)}")
            context = {
                'user': user,
                'role_choices': CustomUser.ROLE_CHOICES,
            }
            return render(request, self.template_name, context)


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