document.addEventListener('DOMContentLoaded', function() {
    const cardsFrame = document.getElementById('cards-frame');
    const umaFrame = document.getElementById('uma-frame');
    const cardsBtn = document.getElementById('cards-btn');
    const umaBtn = document.getElementById('uma-btn');
    
    const imageContainer4 = document.getElementById('image-container');
    const imageContainerUma = document.getElementById('image-container-uma');
    const imageContainer1 = document.getElementById('dynamic-images-1');
    const imageContainer2 = document.getElementById('dynamic-images-2');
    const maxItems = 200;

    // Toggle frame visibility
    function showFrame(frameToShow) {
        if (frameToShow === 'cards') {
            cardsFrame.style.display = 'flex';
            umaFrame.style.display = 'none';
            cardsBtn.classList.add('active');
            umaBtn.classList.remove('active');
        } else if (frameToShow === 'uma') {
            cardsFrame.style.display = 'none';
            umaFrame.style.display = 'flex';
            cardsBtn.classList.remove('active');
            umaBtn.classList.add('active');
        }
    }

    // Button event listeners
    cardsBtn.addEventListener('click', () => showFrame('cards'));
    umaBtn.addEventListener('click', () => showFrame('uma'));

    // Load JSON data for cards
    fetch('support_cards.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch JSON file');
            }
            return response.json();
        })
        .then(data => {
            renderImages(data, imageContainer4);
        })
        .catch(error => {
            console.error('Error loading the JSON data:', error);
        });

    // Load UMA images from folder (you'll need to create a list of image files)
    // For now, I'll show how you can manually add them or load from a different JSON
    function loadUmaImages() {
        // Option 1: Load from a separate JSON file for UMA images
        fetch('assets/uma-data.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch UMA JSON file');
                }
                return response.json();
            })
            .then(umaData => {
                renderImages(umaData, imageContainerUma);
            })
            .catch(error => {
                console.error('Error loading UMA data, trying manual approach:', error);
                // Option 2: Manual list of UMA images (fallback)
                loadUmaImagesManually();
            });
    }

    // Manual UMA image loading (if you don't have a JSON file)
    function loadUmaImagesManually() {
        // You would need to list your UMA image filenames here
        const umaImageFiles = [
            'uma1.png', 'uma2.png', 'uma3.png' // Add your actual filenames
            // ... add more filenames as needed
        ];

        const umaData = umaImageFiles.map((filename, index) => ({
            image: `assets/images/umas/${filename}`,
            alt: `UMA ${index + 1}`,
            name: filename.replace('.png', '').replace('.jpg', '') // Use filename as name
        }));

        renderImages(umaData, imageContainerUma);
    }

    function renderImages(data, container) {
        container.innerHTML = '';

        data.forEach(item => {
            const img = document.createElement('img');
            img.src = item.local_image;
            img.alt = item.alt;
            img.classList.add('card-image');
            img.dataset.name = item.name;
            img.style.display = '';

            container.appendChild(img);
            addImageEventListeners(img);
        });

        updateTotalPercentage();
    }

    function updateTotalPercentage() {
        const frame1Count = imageContainer1.getElementsByTagName('img').length;
        const frame2Count = imageContainer2.getElementsByTagName('img').length;
        const totalImages = frame1Count + frame2Count;
        const percentage = (totalImages / maxItems) * 100;

        document.getElementById('percentage').textContent = `${Math.min(percentage, 100).toFixed(2)}%`;
        document.getElementById('number').textContent = `${totalImages}/${maxItems}`;
    }

    function addImageEventListeners(image) {
        const originalParent = image.parentNode;

        image.addEventListener('click', function(event) {
            if (event.button === 0) {
                if (this.parentNode === originalParent) {
                    const clonedImage = this.cloneNode(true);
                    imageContainer1.appendChild(clonedImage);
                    addCloneEventListeners(clonedImage);
                    updateTotalPercentage();
                } else {
                    this.remove();
                    updateTotalPercentage();
                }
            }
        });

        image.addEventListener('contextmenu', function(event) {
            event.preventDefault();

            if (this.parentNode === originalParent) {
                const clonedImage = this.cloneNode(true);
                imageContainer2.appendChild(clonedImage);
                addCloneEventListeners(clonedImage);
                updateTotalPercentage();
            } else {
                this.remove();
                updateTotalPercentage();
            }
        });
    }

    function addCloneEventListeners(clonedImage) {
        clonedImage.addEventListener('click', function() {
            this.remove();
            updateTotalPercentage();
        });
    }

    // Search functionality for Cards
    const searchBox = document.getElementById('search-box');
    searchBox.addEventListener('input', function() {
        const searchText = searchBox.value.toLowerCase();
        const images = imageContainer4.getElementsByTagName('img');
        
        for (let img of images) {
            const name = img.dataset.name.toLowerCase();
            if (name.includes(searchText)) {
                img.style.display = '';
            } else {
                img.style.display = 'none';
            }
        }
    });

    // Search functionality for UMA
    const searchBoxUma = document.getElementById('search-box-uma');
    searchBoxUma.addEventListener('input', function() {
        const searchText = searchBoxUma.value.toLowerCase();
        const images = imageContainerUma.getElementsByTagName('img');
        
        for (let img of images) {
            const name = img.dataset.name.toLowerCase();
            if (name.includes(searchText)) {
                img.style.display = '';
            } else {
                img.style.display = 'none';
            }
        }
    });

    // Initialize UMA images
    loadUmaImages();

    // Event listeners for percentage updates
    document.addEventListener('click', updateTotalPercentage);
    document.addEventListener('contextmenu', updateTotalPercentage);
});