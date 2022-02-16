from django import forms
#from django.core.exceptions import ValidationError

class XrentanForm(forms.Form):
    toushigaku = forms.CharField(
        label='toushigaku',
        required=True,
        max_length=9,
        min_length=3,
        error_messages={
            'required':'投資額は必須です。',
            'max_length': '* 最大金額を超過しています。',
            'min_length': '* 最小金額を下回っています。'}
    )

    #def clean_body(self):
    #    body = self.cleaned_data['body']
    #    if(body.find('<') != -1 or body.find('>') != -1):
    #        raise forms.ValidationError("Tags are not allowed.")
    #    return body