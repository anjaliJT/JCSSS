
# from .core import compute_all_metrics
from .core import compute_all_metrics, compute_complain, compute_product, compute_user
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

class StatisticsView(View):

    def get(self, request):
        user = request.user

        # Step 1: Compute all statistics
        if user.role != "CUSTOMER":
            full_data = compute_all_metrics(user)
            return render(request,"base.html", full_data)
        
        else:
            # data = compute_projects(user)
            # data = compute_requests(user)
            user_data = compute_complain(user)
            return render(request,"base.html", user_data)

