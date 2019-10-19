from django import forms


class UploadFileForm(forms.Form):
    # file = forms.FileField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))