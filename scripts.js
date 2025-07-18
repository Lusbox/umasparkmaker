const images = {
    filter1: {
        static1: [
            "image1a.jpg",
            "image2a.jpg"
        ],
        static2: [
            "image3a.jpg",
            "image4a.jpg"
        ]
    },
    filter2: {
        static1: [
            "image1b.jpg",
            "image2b.jpg"
        ],
        static2: [
            "image3b.jpg",
            "image4b.jpg"
        ]
    },
    filter3: {
        static1: [
            "image1c.jpg",
            "image2c.jpg"
        ],
        static2: [
            "image3c.jpg",
            "image4c.jpg"
        ]
    }
};

function applyFilter(filter) {
    // Clear the previous dynamic images in both frames
    document.querySelectorAll('.dynamic-images').forEach(container => {
        container.innerHTML = '';
    });

    const filterImages = images[filter];

    // Loop through both static images and load the corresponding dynamic images
    ['static1', 'static2'].forEach((staticImage, index) => {
        const dynamicContainer = document.getElementById(`dynamic-images-${index + 1}`);
        filterImages[staticImage].forEach(image => {
            const imgElement = document.createElement('img');
            imgElement.src = image;
            imgElement.alt = `Dynamic Image: ${image}`;
            dynamicContainer.appendChild(imgElement);
        });
    });
}
