from django import forms
from django.core.exceptions import ValidationError

from apps.common.phone import normalize_phone

from .models import ConsultationRequest, Order

PHONE_PATTERN = r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"


def phone_widget():
    return forms.TextInput(
        attrs={
            "class": "order__form_input",
            "placeholder": "+7 (999) 000-00-00",
            "inputmode": "tel",
            "autocomplete": "tel",
            "pattern": PHONE_PATTERN,
        }
    )


class OrderForm(forms.ModelForm):
    promo = forms.CharField(
        label="Промокод",
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "order__form_input",
                "placeholder": "Введите промокод",
            }
        ),
    )
    consent = forms.BooleanField(
        required=True,
        label="Я согласен(а) с политикой конфиденциальности",
        error_messages={
            "required": "Необходимо согласие с политикой конфиденциальности"
        },
        widget=forms.CheckboxInput(
            attrs={"style": "margin-right: 10px; cursor: pointer;"}
        ),
    )

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
            "customer_phone": phone_widget(),
            "delivery_address": forms.TextInput(
                attrs={
                    "class": "order__form_input",
                    "placeholder": "Адрес доставки",
                }
            ),
            "delivery_time": forms.RadioSelect(),
            "payment_method": forms.RadioSelect(),
        }

    def clean_customer_phone(self):
        value = (self.cleaned_data.get("customer_phone") or "").strip()
        normalized = normalize_phone(value)
        if normalized is None:
            raise ValidationError("Некорректный номер телефона")
        return normalized

    def get_promo(self):
        code = (self.cleaned_data.get("promo") or "").strip()
        return code.upper()


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
            "phone": phone_widget(),
        }

    def clean_phone(self):
        value = (self.cleaned_data.get("phone") or "").strip()
        normalized = normalize_phone(value)
        if normalized is None:
            raise ValidationError("Некорректный номер телефона")
        return normalized
