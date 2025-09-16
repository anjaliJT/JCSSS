from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages  # optional, for error messages
from apps.users.models import CustomUser
from django.views import View
from apps.users.forms import CustomUserSignupForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

import logging

logger = logging.getLogger(__name__)


class Login(View):
    def get(self, request):
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
    
    
class UserDetails(View):
    def get(self, request):
        return render(request, "dashboard.html", {"user": None})

class UserDetails_dummy(View):
    def get(self, request):
        return render(request, "complaints/complaints_main_page.html", {
            "user": None
            # "complaints": []
        })

class profileView(View): 
    def get(self,request):
        context = {
            'user': request.user,
        }

        return render(request,'users/profile.html',context)
    
