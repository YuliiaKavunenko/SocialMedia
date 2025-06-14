document.addEventListener('DOMContentLoaded', function () {
    const createAlbum = document.getElementById('create-albums');
    const albumForm = document.getElementById('create-album-window-background');

    createAlbum.addEventListener('click', function (event) {
        event.preventDefault();
        albumForm.style.display = 'block';
    });
    const closeButton = document.getElementById('close-button');
    if (closeButton) {
        closeButton.addEventListener('click', function (event) {
            event.preventDefault();
            albumForm.style.display = 'none';
        });
    }
});