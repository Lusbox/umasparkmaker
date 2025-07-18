document.addEventListener('DOMContentLoaded', function() {
    // Fetch JSON data
    fetch('assets/data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch JSON file');
            }
            return response.json();
        })
        .then(data => {
            const imageContainer = document.getElementById('image-container'); // Container for original images (frame4)

            // Loop through each item in the JSON data
            data.forEach(item => {
                // Create the image element
                const img = document.createElement('img');
                img.src = item.image;       // Image source from JSON
                img.alt = item.alt;         // Image alt text from JSON
                img.classList.add('card-image');  // Add 'card-image' class for styling

                // Append the image to the original container (frame4)
                imageContainer.appendChild(img);

                // Add event listeners to handle clicks for moving and removing images
                addImageEventListeners(img);
            });
        })
        .catch(error => {
            console.error('Error loading the JSON data:', error);
        });
});

// Function to add event listeners to images
function addImageEventListeners(image) {
    // Store the original image container (frame4)
    const originalParent = image.parentNode;

    // Left-click event to move image to frame2
    image.addEventListener('click', function(event) {
        if (event.button === 0) { // Left-click

            if (this.parentNode === originalParent) {
                // Clone the image and move to frame2
                const clonedImage = this.cloneNode(true);
                document.getElementById('dynamic-images-1').appendChild(clonedImage);
                addCloneEventListeners(clonedImage);  // Attach event listeners to the cloned image
            } else {
                // If already in frame2, remove the cloned image
                this.remove();
            }
        }
    });

    // Right-click event to move image to frame3
    image.addEventListener('contextmenu', function(event) {
        event.preventDefault(); // Prevent right-click menu

        if (this.parentNode === originalParent) {
            // Clone the image and move to frame3
            const clonedImage = this.cloneNode(true);
            document.getElementById('dynamic-images-2').appendChild(clonedImage);
            addCloneEventListeners(clonedImage);  // Attach event listeners to the cloned image
        } else {
            // If already in frame3, remove the cloned image
            this.remove();
        }
    });
}

// Function to add event listeners to cloned images in frame2/frame3
function addCloneEventListeners(clonedImage) {
    clonedImage.addEventListener('click', function() {
        // Remove the cloned image when clicked
        this.remove();
    });
}

// Resize images dynamically when the window is resized or images are added
window.addEventListener('resize', adjustImageSize);

// Function to adjust the size of images based on container width
function adjustImageSize() {
    const containers = [document.getElementById('dynamic-images-1'), document.getElementById('dynamic-images-2')];

    containers.forEach(container => {
        const images = container.querySelectorAll('img');
        const containerWidth = container.clientWidth;

        // Calculate the number of images per row (approx.)
        const imagesPerRow = Math.floor(containerWidth / 150); // 150px as a base width per image (adjust as needed)
        const imageWidth = (containerWidth / imagesPerRow) - 10; // Adjust width based on images per row

        images.forEach(image => {
            image.style.width = `${imageWidth}px`; // Set the width of each image
        });
    });
}
