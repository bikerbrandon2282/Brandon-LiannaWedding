document.addEventListener('DOMContentLoaded', () => {
	const images = Array.from(
		document.querySelectorAll('[data-image-gallery] img, .image-gallery img, #gallery img')
	);
	const button = document.querySelector(
		'[data-load-more], #load-more, #loadMore, .load-more'
	);
	const batchSize = 5;
	let shown = 0;

	if (!images.length) {
		if (button) button.hidden = true;
		return;
	}

	// Defer images after the first batch. Use data-src for lazy image URLs.
	images.forEach((image, index) => {
		if (index >= batchSize) {
			if (image.getAttribute('src')) {
				image.dataset.src = image.getAttribute('src');
				image.removeAttribute('src');
			}
			image.hidden = true;
		}
	});

	function showNextBatch() {
		const end = Math.min(shown + batchSize, images.length);
		while (shown < end) {
			const image = images[shown];
			if (image.dataset.src) {
				image.src = image.dataset.src;
				delete image.dataset.src;
			}
			image.hidden = false;
			shown += 1;
		}

		if (button) button.hidden = shown >= images.length;
	}

	if (button) button.addEventListener('click', showNextBatch);
	showNextBatch();
});
