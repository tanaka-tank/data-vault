from django import forms
#from django.core.exceptions import ValidationError

class FontimageForm(forms.Form):
    build_string = forms.CharField(
        label='build_string',
        required=True,
        max_length=100,
        widget=forms.Textarea,
        error_messages={
            'max_length': '* Input is 100 character limit.',
            'required': '入力項目は必須です。'}
    )

    #def clean_body(self):
    #    body = self.cleaned_data['body']
    #    if(body.find('<') != -1 or body.find('>') != -1):
    #        raise forms.ValidationError("Tags are not allowed.")
    #    return body