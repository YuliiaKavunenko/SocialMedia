document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById("codeModal");
    const overlay = document.getElementById("overlay");
    const closeModalBtn = document.getElementById("closeModal");
    const registerForm = document.getElementById("registrationForm");

    if (modal.classList.contains("show")) {
        modal.style.display = "flex";
        overlay.style.display = "flex";
    }

    // Закриття модалки та оверлею по кнопці "Назад"
    closeModalBtn?.addEventListener("click", function () {
        modal.style.display = "none";
        overlay.style.display = "none";
    });

    // Після натискання на кнопку "Зареєструватися"
    registerForm?.addEventListener("submit", function (event) {
        const form = event.target;

        if (!modal.classList.contains("show")) {
            event.preventDefault();
            form.submit();
        }
    });
});
