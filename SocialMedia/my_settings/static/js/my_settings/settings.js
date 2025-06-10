document.addEventListener("DOMContentLoaded", function () {
    const editBtn = document.getElementById("edit-information2");
    const saveBtn = document.getElementById("save-changes-button");

    const inputs = [
        document.getElementById("name-input"),
        document.getElementById("surname-input"),
        document.getElementById("birth-date-input"),
        document.getElementById("email-input"),
    ];

    editBtn.addEventListener("click", function (event) {
        event.preventDefault();

        inputs.forEach(input => {
            if (input) {
                input.removeAttribute("readonly");
                input.removeAttribute("disabled");
                input.style.border = "1px solid #ccc";
            }
        });

        saveBtn.style.display = "inline-block";
    });
});
