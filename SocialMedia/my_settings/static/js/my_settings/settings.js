document.addEventListener("DOMContentLoaded", () => {
  const editBtn = document.getElementById("edit-information2")
  const saveBtn = document.getElementById("save-changes-button")

  const inputs = [
    document.getElementById("name-input"),
    document.getElementById("surname-input"),
    document.getElementById("birth-date-input"),
    document.getElementById("email-input"),
  ]

  editBtn.addEventListener("click", (event) => {
    event.preventDefault()

    inputs.forEach((input) => {
      if (input) {
        input.removeAttribute("readonly")
        input.removeAttribute("disabled")
        input.style.border = "1px solid #ccc"
      }
    })
    editBtn.style.display = "none"
    saveBtn.style.display = "inline-block"
  })

  const editPasswordBtn = document.getElementById("edit-password")
  const savePasswordBtn = document.getElementById("save-new-password-button")
  const confirmPasswordWrapper = document.getElementById("confirm-password-wrapper")
  const passwordForm = document.getElementById("password-header")

  const newPassword1Input = document.getElementById("id_new_password1")
  const newPassword2Input = document.getElementById("id_new_password2")

  editPasswordBtn.addEventListener("click", (event) => {
    event.preventDefault()

    confirmPasswordWrapper.style.display = "flex"
    ;[newPassword1Input, newPassword2Input].forEach((input) => {
      input.removeAttribute("readonly")
      input.removeAttribute("disabled")
      input.style.border = "1px solid #ccc"
    })

    editPasswordBtn.style.display = "none"
    savePasswordBtn.style.display = "inline-block"
  })

  const editUsernameBtn = document.getElementById("edit-information1")
  const saveUsernameBtn = document.getElementById("save-new-username-button")
  const chooseText = document.getElementById("choose-avatar-text")
  const avatarButtons = document.getElementById("avatar-buttons")
  const staticUsername = document.getElementById("static-username")
  const editUsernameInput = document.getElementById("edit-username-input")

  if (editUsernameBtn) {
    editUsernameBtn.addEventListener("click", (event) => {
      event.preventDefault()
      editUsernameBtn.style.display = "none"
      saveUsernameBtn.style.display = "inline-block"

      chooseText.style.display = "flex"
      avatarButtons.style.display = "flex"
      staticUsername.style.display = "none"
      editUsernameInput.style.display = "flex"
    })
  }
  const uploadInput = document.getElementById("upload-avatar-input")
  const addPhotoBtn = document.getElementById("add-photo-btn")
  const selectPhotoBtn = document.getElementById("select-photo-btn")
  const actionTypeInput = document.getElementById("avatar-action-type")

  addPhotoBtn.addEventListener("click", (event) => {
    event.preventDefault()
    actionTypeInput.value = "add_avatar"
    uploadInput.click()
  })

  selectPhotoBtn.addEventListener("click", (event) => {
    event.preventDefault()
    actionTypeInput.value = "select_avatar"
    uploadInput.click()
  })

  uploadInput.addEventListener("change", () => {
    if (uploadInput.files.length > 0) {
      document.getElementById("profile-header").submit()
    }
  })

  // Переопределяем обработчик для кнопки редактирования пароля
  if (editPasswordBtn) {
    // Удаляем старый обработчик
    editPasswordBtn.replaceWith(editPasswordBtn.cloneNode(true))
    const newEditPasswordBtn = document.getElementById("edit-password")

    newEditPasswordBtn.addEventListener("click", (event) => {
      event.preventDefault()
      console.log("Нажата кнопка редактирования пароля")

      // Отправляем AJAX запрос для отправки кода
      fetch("/ajax/send-password-code/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Ответ сервера:", data)
          if (data.success) {
            // Показываем модалку
            showPasswordModal()
          } else {
            alert("Помилка при відправці коду: " + data.error)
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("Помилка при відправці коду")
        })
    })
  }

  // Добавляем обработчик для формы смены пароля
  if (passwordForm && savePasswordBtn) {
    savePasswordBtn.addEventListener("click", (event) => {
      event.preventDefault()
      console.log("Отправка формы смены пароля")

      // Проверяем, что поля заполнены
      const password1 = newPassword1Input.value.trim()
      const password2 = newPassword2Input.value.trim()

      if (!password1 || !password2) {
        alert("Будь ласка, заповніть всі поля пароля")
        return
      }

      if (password1 !== password2) {
        alert("Паролі не співпадають")
        return
      }

      // Отправляем форму
      passwordForm.submit()
    })
  }

  // Функция показа модального окна
  function showPasswordModal() {
    const passwordOverlay = document.getElementById("password-overlay")
    const passwordModal = document.getElementById("passwordCodeModal")

    if (passwordOverlay && passwordModal) {
      passwordOverlay.style.display = "flex"
      passwordOverlay.classList.add("show")
      passwordModal.classList.add("show")
      console.log("Модальное окно показано")
    } else {
      console.error("Модальное окно не найдено")
    }
  }

  // Функция скрытия модального окна
  function hidePasswordModal() {
    const passwordOverlay = document.getElementById("password-overlay")
    const passwordModal = document.getElementById("passwordCodeModal")

    if (passwordOverlay && passwordModal) {
      passwordOverlay.style.display = "none"
      passwordOverlay.classList.remove("show")
      passwordModal.classList.remove("show")
    }
  }

  // Обработка закрытия модального окна
  const closePasswordModalBtn = document.getElementById("closePasswordModal")
  if (closePasswordModalBtn) {
    closePasswordModalBtn.addEventListener("click", () => {
      hidePasswordModal()
    })
  }

  // Закрытие модального окна при клике вне его
  const passwordOverlay = document.getElementById("password-overlay")
  if (passwordOverlay) {
    passwordOverlay.addEventListener("click", (e) => {
      if (e.target === passwordOverlay) {
        hidePasswordModal()
      }
    })
  }

  // Обработка подтверждения кода
  const passwordCodeForm = document.getElementById("passwordCodeForm")
  if (passwordCodeForm) {
    passwordCodeForm.addEventListener("submit", (event) => {
      event.preventDefault()
      console.log("Отправка кода подтверждения")

      const formData = new FormData(passwordCodeForm)

      fetch(window.location.href, {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (response.redirected) {
            // Если есть редирект, значит код правильный
            // Устанавливаем флаг в localStorage для активации полей после перезагрузки
            localStorage.setItem("activatePasswordFields", "true")
            window.location.href = response.url
          } else {
            return response.text()
          }
        })
        .then((html) => {
          if (html && (html.includes("password_code_error") || html.includes("Неправильний код"))) {
            // Перезагружаем страницу чтобы показать ошибку
            window.location.reload()
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          window.location.reload()
        })
    })
  }

  // Функция активации полей пароля
  function activatePasswordFields() {
    console.log("Активация полей пароля")

    if (confirmPasswordWrapper) {
      confirmPasswordWrapper.style.display = "flex"
    }
    ;[newPassword1Input, newPassword2Input].forEach((input) => {
      if (input) {
        input.removeAttribute("readonly")
        input.removeAttribute("disabled")
        input.style.border = "1px solid #ccc"
      }
    })

    if (editPasswordBtn) {
      editPasswordBtn.style.display = "none"
    }
    if (savePasswordBtn) {
      savePasswordBtn.style.display = "inline-block"
    }
  }

  // Автоматический переход между полями ввода кода
  const passwordCodeInputs = document.querySelectorAll("#password-inputs .code-input")
  passwordCodeInputs.forEach((input, index) => {
    input.addEventListener("input", function () {
      if (this.value.length === 1 && index < passwordCodeInputs.length - 1) {
        passwordCodeInputs[index + 1].focus()
      }
    })

    input.addEventListener("keydown", function (e) {
      if (e.key === "Backspace" && this.value === "" && index > 0) {
        passwordCodeInputs[index - 1].focus()
      }
    })
  })

  // Проверяем флаг активации полей пароля при загрузке страницы
  if (localStorage.getItem("activatePasswordFields") === "true") {
    console.log("Активируем поля пароля после перезагрузки")
    activatePasswordFields()
    localStorage.removeItem("activatePasswordFields") // Удаляем флаг после использования
  }

  // Проверяем, была ли верификация пароля успешной при загрузке страницы
  if (document.body.dataset.passwordVerified === "true") {
    activatePasswordFields()
  }

  // Показываем модальное окно при загрузке страницы, если есть ошибка кода
  if (document.querySelector(".error") && document.getElementById("password-overlay")) {
    showPasswordModal()
  }
})
