from django import forms
from apps.products.models import Product

class productForm(forms.ModelForm): 
    class Meta: 
        model = Product
        exclude = ["product_model"] 
        # fields = "__all__"

class uploadFileForm(forms.Form):
    file = forms.FileField() 