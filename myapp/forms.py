from django import forms
from myapp.models import Users

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if account and password:
            user = Users.objects.filter(Account=account, Password=password, AuthPass=1).first()
            if user is not None:
                print(f"account - {user.AuthPass}")
            #
            if not user:
                raise forms.ValidationError("帳號或密碼錯誤，或尚未啟用驗證")
            # 如果你需要將查到的 user 傳出去
            self.user = user

        return cleaned_data

class registForm(forms.Form):
    Account = forms.CharField(max_length=15)
    UserName = forms.CharField(max_length=40)
    Password = forms.CharField(widget=forms.PasswordInput())
    Email = forms.CharField(max_length=40)
    AuthCode = forms.CharField(max_length=40)
    AuthPass = forms.BooleanField(initial=False, required=False)

    def clean_Account(self):
        account = self.cleaned_data["Account"]
        if not Users.objects.filter(Account=account).exists():
            raise forms.ValidationError("此帳號不存在")
        return account

    def clean_Password(self):
        return self.cleaned_data["Password"]  # 留給 clean() 做帳密配對

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data["Account"]
        password = cleaned_data["Password"]

        if account and password:
            user = Users.objects.filter(Account=account, Password=password).first()
            if not user:
                raise forms.ValidationError("帳號或密碼錯誤")

        return cleaned_data




