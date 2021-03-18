from django import forms
#from django.core.exceptions import ValidationError

class ConvForm(forms.Form):
    convert_before_name = forms.CharField(
        label='before',
        required=False,
        max_length=20000,
        widget=forms.Textarea,
        error_messages={'max_length': '* Input is 20000 character limit.'}
    )

    #def clean_body(self):
    #    body = self.cleaned_data['body']
    #    if(body.find('<') != -1 or body.find('>') != -1):
    #        raise forms.ValidationError("Tags are not allowed.")
    #    return body