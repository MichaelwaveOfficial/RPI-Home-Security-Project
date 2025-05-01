
document.addEventListener('DOMContentLoaded', function () {

    const sortButton = document.querySelector('.sort-button')

    sortButton.addEventListener('click', (event) => {

        event.preventDefault()

        if (sortButton.textContent.trim() === 'Oldest') {
            sortButton.textContent = 'Newest'
        } else {
            sortButton.textContent = 'Oldest'
        }
    })

    // Implement searchbar functionality here. maybe..


    // Selected image, return image filepath.
    document.querySelectorAll('.capture-container').forEach(container => {

        container.addEventListener('click', function() {

            const filename = this.getAttribute('data-filename')

            fetch(`/captures/view/${filename}`)
            .then(response => response.json())
            .then(data => {

                const imageView = document.querySelector('.image-view')

                imageView.innerHTML = `
                <img src="${data.fullpath}" alt="${filename}" class="img" loading="lazy">
                `
            })
        })
    })

})