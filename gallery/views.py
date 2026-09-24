from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PhotoUploadForm
from .models import Photo


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
        {"form": form, "photos": Photo.objects.all()},
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

    return render(request, "gallery/couple_admin.html", {"form": form, "photos": Photo.objects.all()})


@staff_member_required
def delete_photo(request, photo_id):
    if request.method == "POST":
        photo = get_object_or_404(Photo, pk=photo_id)
        photo.delete()
        messages.success(request, "Photo deleted from the gallery.")
    return redirect("couple_admin")
