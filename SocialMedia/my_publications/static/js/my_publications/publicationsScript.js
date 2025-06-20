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
            document.getElementById("new-tag-form-container").style.display = "none";
            document.getElementById("add-tag-button").style.display = "flex";
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

    // Додавання тега
    const addTagButton = document.getElementById("add-tag-button");
    const tagForm = document.getElementById("new-tag-form-container");

    if (addTagButton && tagForm) {
        addTagButton.addEventListener("click", function () {
            addTagButton.style.display = "none";
            tagForm.style.display = "flex";
        });
    }

    const saveNewTag = document.getElementById("submit-new-tag");
    const newTagInput = document.getElementById("new-tag-input");
    const tagsContainer = document.getElementById("tags-container");

    if (saveNewTag && newTagInput && tagsContainer) {
        saveNewTag.addEventListener("click", function () {
            console.log("Кнопка збереження тега натиснута");

            const newTag = newTagInput.value.trim();

            if (!newTag) {
                alert("Будь ласка, введіть тег.");
                return;
            }

            fetch(ADD_TAG_URL, {
                method: "POST",
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    tag: newTag
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    const tagElement = document.createElement("span");
                    tagElement.classList.add("tag-label");
                    tagElement.textContent = data.tag;
                    tagsContainer.insertBefore(tagElement, tagForm);
                    newTagInput.value = "";
                } else {
                    alert("Помилка: " + data.message);
                }
            })
            .catch(error => {
                console.error("Помилка під час збереження тега:", error);
                alert("Щось пішло не так при додаванні тега.");
            });
        });
    }
    // Додавання URL
    const addUrlButton = document.getElementById('add-url-button');
    const submitNewUrlButton = document.getElementById('submit-new-url');
    const newUrlInput = document.getElementById('new-url-input');
    const newUrlFormContainer = document.getElementById('new-url-form-container');
    const urlsList = document.getElementById('urls-list');

    addUrlButton.addEventListener('click', function () {
        addUrlButton.style.display = 'none';
        newUrlFormContainer.style.display = 'flex';
        newUrlInput.focus();
    });

    submitNewUrlButton.addEventListener('click', function () {
        const urlValue = newUrlInput.value.trim();
        if (urlValue !== '') {
            // створюємо новий input з цим URL
            const newInput = document.createElement('input');
            newInput.type = 'text';
            newInput.name = 'extra_urls';
            newInput.value = urlValue;
            newInput.readOnly = true;
            newInput.classList.add('url-input-added');
            urlsList.appendChild(newInput);

            // очищаємо поле
            newUrlInput.value = '';
            newUrlFormContainer.style.display = 'none';
            addUrlButton.style.display = 'flex';
        }
    });

    const tagLabels = document.querySelectorAll(".tag-label");
    const hiddenInput = document.getElementById("selected-tags-input");

    let selectedTagIds = new Set();

    tagLabels.forEach(tag => {
        tag.addEventListener("click", function () {
            const tagId = this.getAttribute("data-tag-id");

            if (this.classList.contains("selected")) {
                this.classList.remove("selected");
                selectedTagIds.delete(tagId);
            } else {
                this.classList.add("selected");
                selectedTagIds.add(tagId);
                
            }

            hiddenInput.value = Array.from(selectedTagIds).join(",");
        });
    });

    const addImageButton = document.getElementById("add-image-button");
    const imageInput = document.getElementById("id_images");

    if (addImageButton && imageInput) {
        addImageButton.addEventListener("click", function (event) {
            event.preventDefault();
            imageInput.click();
        });

        imageInput.addEventListener("change", function () {
            if (imageInput.files.length > 0) {
                console.log("Вибраний файл:", imageInput.files[0].name);
            }
        });
    } else {
        console.warn("Не знайдено кнопку або інпут для вибору файлу");
    }

});