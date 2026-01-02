from django import forms
from apps.products.models import Product, Product_model

# class productForm(forms.ModelForm):
#     product_model = forms.ModelChoiceField(
#         queryset=Product_model.objects.all(),
#         required=True
#     )

#     class Meta:
#         model = Product
#         fields = "__all__"
class productForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_model",
            "tail_number",
            "contract_number",
            "delivery_date",
            "delivery_location",
            "current_location",
            "army_command",
            "active_status",
            "unit_name",
            "formation",
            "warranty_period",
            "remarks",
        ]
        widgets = {
            "active_status": forms.Select(
                choices=[(True, "Active"), (False, "Discontinued")],
                attrs={"class": "form-select"}
            )
        }


class uploadFileForm(forms.Form):
    file = forms.FileField() 