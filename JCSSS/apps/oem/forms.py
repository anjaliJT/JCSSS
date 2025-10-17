# forms.py
from django import forms
from .models import ComplaintStatus, RepairCost, CustomerPricing

class ComplaintStatusForm(forms.ModelForm):
    class Meta:
        model = ComplaintStatus
        fields = ['status', 'remarks', 'attachments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachments': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class RepairCostForm(forms.ModelForm):
    class Meta:
        model = RepairCost
        fields = ["description", "repair_cost", "attachment"]
        widgets = {
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Describe the repair work..."
            }),
            "repair_cost": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "min": "0",
                "step": "0.01"
            }),
            "attachment": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }
        labels = {
            "description": "Repair Description",
            "cost": "Repair Cost (₹)",
            "attachment": "Attachment (Optional)",
        }

class CustomerPricingForm(forms.ModelForm):
    class Meta:
        model = CustomerPricing
        fields = ['total_price', 'invoice']