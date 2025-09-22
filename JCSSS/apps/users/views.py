from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages  # optional, for error messages
from apps.users.models import CustomUser
from django.views import View
from apps.users.forms import CustomUserSignupForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.contrib.auth import logout

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