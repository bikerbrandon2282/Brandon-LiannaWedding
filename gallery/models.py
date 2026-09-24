from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Photo(models.Model):
    title = models.CharField(max_length=120, blank=True)
    image = models.FileField(
        upload_to="gallery/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "gif", "webp"])],
    )
    cloudinary_url = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_url(self):
        if self.cloudinary_url:
            return self.cloudinary_url
        if settings.CLOUDINARY_URL:
            from cloudinary.utils import cloudinary_url

            return cloudinary_url(self.image.name, secure=True, resource_type="image")[0]
        return self.image.url

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title or self.image.name.rsplit("/", 1)[-1]

    def delete(self, *args, **kwargs):
        image_storage = self.image.storage
        image_name = self.image.name
        super().delete(*args, **kwargs)
        if image_name:
            image_storage.delete(image_name)
