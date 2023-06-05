from django import forms

from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code']

        widgets = {
            'code': forms.TextInput(attrs={"placeholder": 'Coupon code...'})
        }
        
