
document.addEventListener('DOMContentLoaded', function () {

    const nameSearch = document.getElementById('search-bar')
    nameSearch.addEventListener('input', () => filterProjects(nameSearch))

})


function filterProjects(searchInput) {

    const captures = document.querySelectorAll('.capture-container');
    const query = searchInput.value.toLowerCase();

    captures.forEach((capture) => {
        const name = capture.getAttribute('data-item').toLowerCase();
        const match = name.includes(query);

        capture.style.display = match ? '' : 'none';
    });
}
