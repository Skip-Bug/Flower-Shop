from django import forms

from .models import ConsultationRequest, Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "customer_name",
            "customer_phone",
            "delivery_address",
            "delivery_time",
            "payment_method",
        ]
        widgets = {
            "customer_name": forms.TextInput(
                attrs={
                    "class": "order__form_input",
                    "placeholder": "Введите Имя",
                }
            ),
            "customer_phone": forms.TextInput(
                attrs={
                    "class": "order__form_input",
                    "placeholder": "+ 7 (999) 000 00 00",
                }
            ),
            "delivery_address": forms.TextInput(
                attrs={
                    "class": "order__form_input",
                    "placeholder": "Адрес доставки",
                }
            ),
            "delivery_time": forms.RadioSelect(),
            "payment_method": forms.RadioSelect(),
        }


class ConsultationRequestForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label="Я согласен(а) с политикой конфиденциальности",
        widget=forms.CheckboxInput(attrs={"class": "singUpConsultation__ckekbox"}),
    )

    class Meta:
        model = ConsultationRequest
        fields = ["customer_name", "phone"]
        widgets = {
            "customer_name": forms.TextInput(
                attrs={
                    "class": "order__form_input",
                    "placeholder": "Введите Имя",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "order__form_input",
                    "placeholder": "+ 7 (999) 000 00 00",
                }
            ),
        }
