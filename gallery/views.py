import json
import logging

from cloudinary import api as cloudinary_api
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PhotoUploadForm
from .models import Photo

logger = logging.getLogger(__name__)


def cloudinary_upload_context():
    return {
        "cloudinary_cloud_name": settings.CLOUDINARY_CLOUD_NAME,
        "cloudinary_upload_preset": settings.CLOUDINARY_UPLOAD_PRESET,
    }


def delete_cloudinary_photo(public_id):
    try:
        cloudinary_api.delete_resources([public_id], resource_type="image", type="upload")
        return True
    except Exception:
        logger.exception("Could not delete duplicate Cloudinary photo %s.", public_id)
        return False


def sync_cloudinary_photos():
    if not settings.CLOUDINARY_URL:
        return

    next_cursor = None
    try:
        while True:
            options = {
                "type": "upload",
                "resource_type": "image",
                "max_results": 500,
            }
            if next_cursor:
                options["next_cursor"] = next_cursor

            response = cloudinary_api.resources(**options)
            for resource in response.get("resources", []):
                public_id = resource.get("public_id")
                secure_url = resource.get("secure_url")
                etag = resource.get("etag", "")
                if not public_id or not secure_url:
                    continue

                photo = Photo.objects.filter(image=public_id).first()
                duplicate = (
                    Photo.objects.filter(cloudinary_etag=etag)
                    .exclude(image=public_id)
                    .first()
                    if etag
                    else None
                )
                if duplicate:
                    if delete_cloudinary_photo(public_id) and photo:
                        Photo.objects.filter(pk=photo.pk).delete()
                    continue
                if photo is None:
                    Photo.objects.create(
                        image=public_id,
                        cloudinary_url=secure_url,
                        cloudinary_etag=etag,
                    )
                elif photo.cloudinary_url != secure_url or photo.cloudinary_etag != etag:
                    photo.cloudinary_url = secure_url
                    photo.cloudinary_etag = etag
                    photo.save(update_fields=["cloudinary_url", "cloudinary_etag"])

            next_cursor = response.get("next_cursor")
            if not next_cursor:
                break
    except Exception:
        logger.exception("Could not synchronize photos from Cloudinary.")


@require_POST
def record_cloudinary_photo(request):
    if not settings.CLOUDINARY_URL:
        return JsonResponse({"error": "Cloudinary uploads are not configured."}, status=503)

    try:
        payload = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid upload data."}, status=400)

    public_id = payload.get("public_id")
    cloudinary_url = payload.get("secure_url")
    etag = payload.get("etag", "")
    title = payload.get("title", "")
    if not isinstance(public_id, str) or not public_id.strip():
        return JsonResponse({"error": "Cloudinary did not return an image id."}, status=400)
    if not isinstance(cloudinary_url, str) or not cloudinary_url.startswith("https://"):
        return JsonResponse({"error": "Cloudinary did not return a usable image URL."}, status=400)
    if not isinstance(etag, str):
        etag = ""

    existing = Photo.objects.filter(image=public_id).first()
    if existing:
        existing.cloudinary_url = cloudinary_url
        existing.cloudinary_etag = etag
        existing.save(update_fields=["cloudinary_url", "cloudinary_etag"])
        return JsonResponse({"id": existing.id})

    duplicate = Photo.objects.filter(cloudinary_etag=etag).exclude(image=public_id).first() if etag else None
    if duplicate:
        if not delete_cloudinary_photo(public_id):
            return JsonResponse({"error": "The duplicate image could not be removed."}, status=503)
        return JsonResponse({"duplicate": True, "id": duplicate.id})

    photo = Photo.objects.create(
        title=title[:120] if isinstance(title, str) else "",
        image=public_id,
        cloudinary_url=cloudinary_url,
        cloudinary_etag=etag,
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

    sync_cloudinary_photos()
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

    sync_cloudinary_photos()
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
