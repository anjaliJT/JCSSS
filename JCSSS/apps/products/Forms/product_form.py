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
            "order_name",
            "manufecturing_Date",
            "delivery_location",
            "army_command",
            "unit_name",
            "formation",
            "warranty_period",
        ]


class uploadFileForm(forms.Form):
    file = forms.FileField() 