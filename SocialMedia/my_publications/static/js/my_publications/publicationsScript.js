document.addEventListener("DOMContentLoaded", function () {
    // Створення публікації
    const openBtn = document.getElementById("publication-button");
    const modal = document.getElementById("create-publication-form-background");
    const closeBtn = document.getElementById("close-button");

    if (openBtn && modal && closeBtn) {
        openBtn.addEventListener("click", function (event) {
            event.preventDefault();
            modal.style.display = "flex";
            const PublicationsTextArea = document.getElementById("new-publication-input").value;
            document.getElementById("form-text").value = PublicationsTextArea;
        });

        closeBtn.addEventListener("click", function (event) {
            event.preventDefault();
            modal.style.display = "none";
        });
    }

    // Відкриття/закриття меню з трьома крапками
    document.querySelectorAll('.publication-dots').forEach(button => {
        button.addEventListener('click', function () {
            const menu = this.parentElement.querySelector('.dots-menu');
            const isVisible = menu.style.display === 'flex';
            menu.style.display = isVisible ? 'none' : 'flex';
            this.style.backgroundColor = isVisible ? '#FFFFFF' : '#E9E5EE';
        });
    });

    // Відкриття форми редагування публікації
    document.querySelectorAll('.dots-menu-button.edit').forEach(btn => {
        btn.addEventListener('click', function (event) {
            event.preventDefault();
            // Закриваємо меню з трьома крапками
            const allMenus = document.querySelectorAll('.dots-menu');
            allMenus.forEach(menu => {
                menu.style.display = 'none';
            });
            const allDotsButtons = document.querySelectorAll('.publication-dots');
            allDotsButtons.forEach(dot => {
                dot.style.backgroundColor = '#FFFFFF';
            });

            const pubId = btn.getAttribute('data-id');
            const formBackground = document.getElementById(`edit-publication-form-background-${pubId}`);
            if (formBackground) {
                formBackground.style.display = 'flex';
                const publicationCard = btn.closest('.publication-card');

                // Витягуємо дані з data-атрибутів
                const title = publicationCard.getAttribute('data-title');
                const theme = publicationCard.getAttribute('data-theme');
                const tags = publicationCard.getAttribute('data-tags');
                const text = publicationCard.getAttribute('data-text');
                const url = publicationCard.getAttribute('data-url');

                // Витягуємо форму редагування по id
                const form = formBackground.querySelector('form');

                // Вставляємо значення в інпути за їх id
                form.querySelector('#form-title').value = title;
                form.querySelector('#form-theme').value = theme;
                form.querySelector('#form-tags').value = tags;
                form.querySelector('#form-text').value = text;
                form.querySelector('#form-url').value = url;


            } else {
                console.warn('Не знайдено форму редагування для id:', pubId);
            }
        });
    });

    // Закриття форми редагування при кліку поза нею
    document.querySelectorAll('.edit-publication-form-background').forEach(formBg => {
        formBg.addEventListener('click', function (event) {
            if (event.target === formBg) {
                formBg.style.display = 'none';
            }
        });
    });

    // Кнопка закриття форми редагування
    document.querySelectorAll('.edit-close-button').forEach(closeBtn => {
        closeBtn.addEventListener('click', function (event) {
            event.preventDefault();
            const parentForm = closeBtn.closest('.edit-publication-form-background');
            if (parentForm) {
                parentForm.style.display = 'none';
            }
        });
    });

    // Обробка кнопки видалення публікації
    document.querySelectorAll('.dots-menu-button.delete').forEach(btn => {
        btn.addEventListener('click', function (event) {
            event.preventDefault();
            const pubId = btn.getAttribute('data-id');
            if (confirm('Ви впевнені, що хочете видалити цю публікацію?')) {
                const form = document.getElementById(`delete-publication-form-${pubId}`);
                if (form) {
                    form.submit();
                }
            }
        });
    });
    document.getElementById("add-tag-button").addEventListener("click", function () {
        document.getElementById("new-tag-input-wrapper").style.display = "block";
        document.getElementById("new-tag-input").focus();
        document.getElementById("add-tag-button").style.display = "none";
    });
    document.getElementById('save-neww-tag').addEventListener("click", function () {
        document.getElementById("new-tag-input-wrapper").style.display = "none";
        document.getElementById("new-tag-input").style.display = "none";
        document.getElementById("add-tag-button").style.display = "block";
    });
});