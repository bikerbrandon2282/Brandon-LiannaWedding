(() => {
    const form = document.querySelector("#photo-upload-form");
    if (!form) return;

    const cloudName = form.dataset.cloudinaryCloudName;
    const uploadPreset = form.dataset.cloudinaryUploadPreset;
    if (!cloudName || !uploadPreset) return;

    const fileInput = form.querySelector('input[type="file"]');
    const submitButton = form.querySelector('button[type="submit"]');
    const status = form.querySelector(".upload-status");
    const titleInput = form.querySelector('input[name="title"]');
    const recordUrl = form.dataset.recordUploadUrl;
    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

    const uploadOne = async (file, title) => {
        const uploadData = new FormData();
        uploadData.append("file", file);
        uploadData.append("upload_preset", uploadPreset);

        const cloudinaryResponse = await fetch(
            `https://api.cloudinary.com/v1_1/${encodeURIComponent(cloudName)}/image/upload`,
            { method: "POST", body: uploadData },
        );
        if (!cloudinaryResponse.ok) throw new Error("Cloudinary upload failed.");

        const cloudinaryPhoto = await cloudinaryResponse.json();
        const recordResponse = await fetch(recordUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ public_id: cloudinaryPhoto.public_id, title }),
        });
        if (!recordResponse.ok) throw new Error("The gallery record could not be saved.");
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const files = Array.from(fileInput.files);
        if (!files.length) return;

        const title = titleInput.value;
        let completed = 0;
        let nextFile = 0;
        let failure;
        submitButton.disabled = true;
        status.textContent = `Uploading 0 of ${files.length} photos...`;

        const worker = async () => {
            while (nextFile < files.length && !failure) {
                const file = files[nextFile++];
                try {
                    await uploadOne(file, title);
                    completed += 1;
                    status.textContent = `Uploading ${completed} of ${files.length} photos...`;
                } catch (error) {
                    failure = error;
                }
            }
        };

        await Promise.all(Array.from({ length: Math.min(4, files.length) }, worker));
        if (failure) {
            status.textContent = `${completed} photos uploaded. ${failure.message}`;
            submitButton.disabled = false;
            return;
        }

        window.location.reload();
    });
})();
