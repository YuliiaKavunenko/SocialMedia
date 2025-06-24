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
        editBtn.style.display = "none";
        saveBtn.style.display = "inline-block";
    });

    const editPasswordBtn = document.getElementById("edit-password");
    const savePasswordBtn = document.getElementById("save-new-password-button");
    const confirmPasswordWrapper = document.getElementById("confirm-password-wrapper");

    const newPassword1Input = document.getElementById("id_new_password1");
    const newPassword2Input = document.getElementById("id_new_password2");

    editPasswordBtn.addEventListener("click", function (event) {
        event.preventDefault();

        confirmPasswordWrapper.style.display = "flex";

        [newPassword1Input, newPassword2Input].forEach(input => {
            input.removeAttribute("readonly");
            input.removeAttribute("disabled");
            input.style.border = "1px solid #ccc";
        });

        editPasswordBtn.style.display = "none";
        savePasswordBtn.style.display = "inline-block";
    });

    const editUsernameBtn = document.getElementById("edit-information1");
    const saveUsernameBtn = document.getElementById("save-new-username-button");
    const chooseText = document.getElementById("choose-avatar-text");
    const avatarButtons = document.getElementById("avatar-buttons");
    const staticUsername = document.getElementById("static-username");
    const editUsernameInput = document.getElementById("edit-username-input");

    if (editUsernameBtn) {
        editUsernameBtn.addEventListener("click", (event) => {
            event.preventDefault();
            editUsernameBtn.style.display = "none";
            saveUsernameBtn.style.display = "inline-block";

            chooseText.style.display = "flex";
            avatarButtons.style.display = "flex";
            staticUsername.style.display = "none";
            editUsernameInput.style.display = "flex";
        });
    }
    const uploadInput = document.getElementById("upload-avatar-input");
    const addPhotoBtn = document.getElementById("add-photo-btn");
    const selectPhotoBtn = document.getElementById("select-photo-btn");
    const actionTypeInput = document.getElementById("avatar-action-type");

    addPhotoBtn.addEventListener("click", (event) => {
        event.preventDefault(); 
        actionTypeInput.value = "add_avatar";
        uploadInput.click();
    });

    selectPhotoBtn.addEventListener("click", (event) => {
        event.preventDefault();
        actionTypeInput.value = "select_avatar";
        uploadInput.click();
    });

    uploadInput.addEventListener("change", () => {
        if (uploadInput.files.length > 0) {
            document.getElementById("profile-header").submit();
        }
    });


});

