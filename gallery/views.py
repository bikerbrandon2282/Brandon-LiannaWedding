import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PhotoUploadForm
from .models import Photo


def cloudinary_upload_context():
    return {
        "cloudinary_cloud_name": settings.CLOUDINARY_CLOUD_NAME,
        "cloudinary_upload_preset": settings.CLOUDINARY_UPLOAD_PRESET,
    }


@require_POST
def record_cloudinary_photo(request):
    if not settings.CLOUDINARY_URL:
        return JsonResponse({"error": "Cloudinary uploads are not configured."}, status=503)

    try:
        payload = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid upload data."}, status=400)

    public_id = payload.get("public_id")
    title = payload.get("title", "")
    if not isinstance(public_id, str) or not public_id.strip():
        return JsonResponse({"error": "Cloudinary did not return an image id."}, status=400)

    photo = Photo.objects.create(
        title=title[:120] if isinstance(title, str) else "",
        image=public_id,
    )
    return JsonResponse({"id": photo.id})


def gallery(request):
    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            for image in form.cleaned_data["images"]:
                Photo.objects.create(title=title, image=image)
            count = len(form.cleaned_data["images"])
            messages.success(request, f"{count} photo{'' if count == 1 else 's'} added to the gallery.")
            return redirect("gallery")
    else:
        form = PhotoUploadForm()

    return render(
        request,
        "gallery/index.html",
        {"form": form, "photos": Photo.objects.all(), **cloudinary_upload_context()},
    )


@staff_member_required
def couple_admin(request):
    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"] or "Uploaded by the couple"
            for image in form.cleaned_data["images"]:
                Photo.objects.create(title=title, image=image)
            count = len(form.cleaned_data["images"])
            messages.success(request, f"{count} photo{'' if count == 1 else 's'} uploaded.")
            return redirect("couple_admin")
    else:
        form = PhotoUploadForm(initial={"title": "Uploaded by the couple"})

    return render(
        request,
        "gallery/couple_admin.html",
        {"form": form, "photos": Photo.objects.all(), **cloudinary_upload_context()},
    )


@staff_member_required
def delete_photo(request, photo_id):
    if request.method == "POST":
        photo = get_object_or_404(Photo, pk=photo_id)
        photo.delete()
        messages.success(request, "Photo deleted from the gallery.")
    return redirect("couple_admin")
