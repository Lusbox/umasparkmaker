document.addEventListener('DOMContentLoaded', function() {
    fetch('assets/data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch JSON file');
            }
            return response.json();
        })
        .then(data => {
            const imageContainer4 = document.getElementById('image-container');
            const imageContainer1 = document.getElementById('dynamic-images-1');
            const imageContainer2 = document.getElementById('dynamic-images-2');
            const totalPercentageElement = document.getElementById('total-percentage');
            const maxItems = 200;


            function renderImages() {
                imageContainer4.innerHTML = '';

                data.forEach(item => {
                    const img = document.createElement('img');
                    img.src = item.image;
                    img.alt = item.alt;
                    img.classList.add('card-image');
                    img.dataset.name = item.name;
                    img.style.display = '';

                    imageContainer4.appendChild(img);
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
                        } else {
                            this.remove();
                        }
                    }
                });

                image.addEventListener('contextmenu', function(event) {
                    event.preventDefault();

                    if (this.parentNode === originalParent) {
                        const clonedImage = this.cloneNode(true);
                        imageContainer2.appendChild(clonedImage);
                        addCloneEventListeners(clonedImage);
                    } else {
                        this.remove();
                    }
                });
            }

            function addCloneEventListeners(clonedImage) {
                clonedImage.addEventListener('click', function() {
                    this.remove();
                    updateTotalPercentage();
                });
            }

            renderImages();

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

                updateTotalPercentage();
            });

            document.addEventListener('click', updateTotalPercentage);
            document.addEventListener('contextmenu', updateTotalPercentage);

        })
        .catch(error => {
            console.error('Error loading the JSON data:', error);
        });
});
