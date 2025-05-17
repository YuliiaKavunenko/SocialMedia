document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("publication-button");
    const modal = document.getElementById("create-publication-form-background");
    const closeBtn = document.getElementById("close-button");

    if (openBtn && modal && closeBtn) {
        openBtn.addEventListener("click", function (event) {
            event.preventDefault();
            modal.style.display = "flex";
        });

        closeBtn.addEventListener("click", function (event) {
            event.preventDefault();
            modal.style.display = "none";
        });
    }
    document.querySelectorAll('.publication-dots').forEach(button => {
        button.addEventListener('click', function () {
            const menu = this.nextElementSibling;
            const isVisible = menu.style.display === 'flex';
            menu.style.display = isVisible ? 'none' : 'flex';
            this.style.backgroundColor = isVisible ? '#FFFFFF' : '#E9E5EE';
        });
    });
});
