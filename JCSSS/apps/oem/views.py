from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import  ComplaintStatus
from apps.complain_form.models import Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db import IntegrityError
from django.contrib import messages



