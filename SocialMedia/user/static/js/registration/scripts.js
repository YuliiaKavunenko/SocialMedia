document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById("codeModal");
    const overlay = document.getElementById("overlay");
    const closeModalBtn = document.getElementById("closeModal");
    const registerForm = document.getElementById("registrationForm");

    // Відкрити модалку, якщо show_modal == True (з сервера)
    if (modal.classList.contains("show")) {
        modal.style.display = "flex";
        overlay.style.display = "flex"; // додали відкриття оверлею
    }

    // Закриття модалки та оверлею по кнопці "Назад"
    closeModalBtn?.addEventListener("click", function () {
        modal.style.display = "none";
        overlay.style.display = "none"; // додали закриття оверлею
    });

    // Після натискання на кнопку "Зареєструватися"
    registerForm?.addEventListener("submit", function (event) {
        const form = event.target;

        // Якщо модалка ще не показана (тобто форма реєстрації), то блокуємо submit
        if (!modal.classList.contains("show")) {
            event.preventDefault();
            form.submit(); // звичайний POST, щоб сервер рендерив show_modal
        }
    });
});
