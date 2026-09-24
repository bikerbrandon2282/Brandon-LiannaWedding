from django import forms
from django.core.validators import FileExtensionValidator

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            raise forms.ValidationError("Choose at least one image to upload.")
        if isinstance(data, (list, tuple)):
            clean_file = super().clean
            return [clean_file(item, initial) for item in data]
        return [super().clean(data, initial)]


class PhotoUploadForm(forms.Form):
    title = forms.CharField(
        required=False,
        label="Photo title (optional)",
        widget=forms.TextInput(attrs={"placeholder": "Photo title (optional)"}),
    )
    images = MultipleFileField(
        label="Images",
        widget=MultipleFileInput(attrs={"accept": "image/*"}),
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "gif", "webp"])],
    )
