from django import forms
from captcha.fields import CaptchaField

class RegisterForm(forms.Form):
    username = forms.CharField(label="輸入帳號")
    email = forms.EmailField(label="電子郵件")
    password1 = forms.CharField(label="輸入密碼", widget=forms.PasswordInput)
    password2 = forms.CharField(label="確認密碼", widget=forms.PasswordInput)
    role = forms.ChoiceField(label="身分類別", choices=[('user', '使用者'), ('owner', '業主')])
    captcha = CaptchaField(label="驗證碼")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("兩次輸入的密碼不一致！")

        return cleaned_data
