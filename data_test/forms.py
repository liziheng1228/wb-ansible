from django import forms
from .models import Host

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['hostname', 'ip', 'port', 'username']  # 如果有密码，加上'password'
