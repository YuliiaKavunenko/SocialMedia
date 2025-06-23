document.addEventListener('DOMContentLoaded', function () {
    const createAlbum = document.getElementById('create-albums');
    const albumForm = document.getElementById('create-album-window-background');
    const editForm = document.getElementById('edit-album-window-background');

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

    // при натисканні на кнопку відкриваємо вибір файлу
    document.querySelectorAll('.add-photo-button').forEach(button => {
        button.addEventListener('click', function () {
            const albumId = this.dataset.albumId;
            const input = document.querySelector(`.photo-input[data-album-id="${albumId}"]`);
            input.click(); // відкриває вікно вибору
        });
    });

    // коли користувач обрав файл
    document.querySelectorAll('.photo-input').forEach(input => {
        input.addEventListener('change', function () {
            const albumId = this.dataset.albumId;
            const file = this.files[0];

            if (!file) return;

            const formData = new FormData();
            formData.append('album_id', albumId);
            formData.append('file', file);

            fetch('/ajax/upload-photo/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const container = document.getElementById(`photo-list-${albumId}`) || this.closest('.photo-list');
                    const img = document.createElement('img');
                    img.src = data.image_url;
                    img.alt = data.filename;
                    container.appendChild(img);
                } else {
                    alert(data.error || 'Помилка при завантаженні фото');
                }
            });
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(';');
            for (let c of cookies) {
                const cookie = c.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.querySelectorAll('.cancel').forEach(cancelButton =>{
        cancelButton.addEventListener('click', function (event) {
            event.preventDefault();
            albumForm.style.display = 'none';
            editForm.style.display = 'none';

        });
    });

    const buttons = document.querySelectorAll('.delete-album-button');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.textContent = '🗑';
        });

        button.addEventListener('mouseleave', () => {
            button.textContent = '👁';
        });
    });


    function handleAlbumDeleteClick(button) {
        const albumId = button.dataset.albumId;

        if (confirm('Ви впевнені, що хочете видалити цей альбом?')) {
            fetch('/ajax/delete-album/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ album_id: albumId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    button.closest('.album-content').remove();
                } else {
                    alert(data.error || 'Не вдалося видалити альбом');
                }
            });
        }
    }

    document.querySelectorAll('.delete-album-button').forEach(button => {
        button.addEventListener('click', function () {
            handleAlbumDeleteClick(this);
        });
    });

    document.querySelectorAll('.delete-album-in-menu-button').forEach(button => {
        button.addEventListener('click', function () {
            handleAlbumDeleteClick(this);
        });
    });


    // відкриття меню до альбому
    const albumMenuBtn = document.querySelectorAll('.open-album-menu');

    albumMenuBtn.forEach(button => {
        const albumContent = button.closest('.album-content');
        const menu = albumContent.querySelector('.album-menu');

        button.addEventListener('click', function () {
        if (menu.style.display === 'flex') {
            menu.style.display = 'none';
            button.style.backgroundColor = '#FFFFFF';
        } else {
            menu.style.display = 'flex';
            button.style.backgroundColor = '#E9E5EE';
        }
        });
    });
    
    // для редагування альбома 
    document.querySelectorAll('.edit-album-button').forEach(button => {
        button.addEventListener('click', () => {
            const albumId = button.dataset.albumId;
            const albumBlock = button.closest('.album-content');
            const name = albumBlock.querySelector('.album-header-name').innerText;
            const topic = albumBlock.querySelector('.theme-and-year h4').innerText;
            // const year = albumBlock.querySelector('.theme-and-year h5').innerText;

            document.querySelector('#edit-album-id').value = albumId;
            // console.log(document.querySelector('#edit-album-id').value);
            // console.log(albumId);
            document.querySelector('#edit-name-input').value = name;
            document.querySelector('#edit-topic-input').value = topic;
            // document.querySelector('#id_year').value = year;

            document.querySelector('#edit-album-window-background').style.display = 'block';
            document.querySelectorAll('.album-menu').forEach(menu => {
                menu.style.display = 'none';
                document.querySelectorAll('.open-album-menu').forEach(buttonOpenMenu => {
                    buttonOpenMenu.style.backgroundColor = '#FFFFFF';
                });
            })
        });
    });

    // Закриття модалки редагування
    document.querySelector('#exit-edit p').addEventListener('click', () => {
        document.querySelector('#edit-album-window-background').style.display = 'none';
    });

    
    const userAddPhotoBtn = document.getElementById('add-photo');
    const userMainAddBtn = document.getElementById('add-user-photo-main');
    const userPhotoInput = document.getElementById('user-photo-input');
    const userPhotoList = document.getElementById('user-photo-list');

    [userAddPhotoBtn, userMainAddBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                userPhotoInput.click();
            });
        }
    });

    if (userPhotoInput) {
        userPhotoInput.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            fetch('/ajax/upload-user-photo/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const img = document.createElement('img');
                    img.src = data.image_url;
                    img.alt = 'avatar';
                    userPhotoList.insertBefore(img, userMainAddBtn);
                } else {
                    alert(data.error || 'Помилка при завантаженні');
                }
            });
        });
    }

    

});