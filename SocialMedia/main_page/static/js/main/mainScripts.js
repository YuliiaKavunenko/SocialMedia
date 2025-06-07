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

    // генерація імені користувача
    const trigger = document.getElementById('suggest-username-trigger');
    const firstNameInput = document.querySelector('input[name="first_name"]');
    const lastNameInput = document.querySelector('input[name="last_name"]');
    const usernameInput = document.querySelector('input[name="username"]');

    function generateUsername() {
        const first = firstNameInput.value.trim().toLowerCase();
        const last = lastNameInput.value.trim().toLowerCase();
        if (!first || !last) {
            document.getElementById('username-generation-error').style.display = 'block';
            document.getElementById('username-generation-error').textContent = 'Заповніть ім’я та прізвище перед генерацією імені користувача';
            return;
        }
        
        const base = (last + first).replace(/\s+/g, '');
        const randomSuffix = Math.floor(100 + Math.random() * 900);
        const suggested = (base + randomSuffix).slice(0, 15);

        usernameInput.value = suggested;
    }

    trigger.addEventListener('click', generateUsername);
});
