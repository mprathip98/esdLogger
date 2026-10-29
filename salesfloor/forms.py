from django import forms
from .models import testLogs, verification

class testLogsForm(forms.ModelForm):
    class Meta:
        model = testLogs
        #placeholders for
        fields = ["username", "otherUser", "date", "time", "station", "testResult"]


class verificationForm(forms.ModelForm):
    class Meta:
        model = verification
        #placeholders for
        fields = ["date", "initials"]
