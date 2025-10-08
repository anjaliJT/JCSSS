from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages  # optional, for error messages
from apps.users.models import CustomUser, ForgotPasswordOTP
from django.views import View
from apps.users.forms import CustomUserSignupForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from datetime import datetime, timedelta, timezone
import logging
import random
import json


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