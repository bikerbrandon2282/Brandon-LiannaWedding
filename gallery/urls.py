from django.urls import path

from .views import couple_admin, delete_photo, gallery, record_cloudinary_photo

urlpatterns = [
    path("", gallery, name="gallery"),
    path("upload/cloudinary/", record_cloudinary_photo, name="record_cloudinary_photo"),
    path("couple-admin/", couple_admin, name="couple_admin"),
    path("couple-admin/delete/<int:photo_id>/", delete_photo, name="delete_photo"),
]
