document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("delete-user-modal")
  const modalOverlay = document.querySelector(".modal-overlay")
  const closeBtn = document.querySelector(".modal-close")
  const cancelBtn = document.querySelector(".cancel-delete-user")
  const confirmBtn = document.querySelector(".confirm-delete-user")

  const deleteButtons = document.querySelectorAll(".delete-request, .delete-recommendation, .delete-friend")
  const confirmButtons = document.querySelectorAll(".confirm-request")
  const addButtons = document.querySelectorAll(".add-recommendation")

  let currentUserToDelete = null
  let currentAction = null

  // Функция для получения CSRF токена
  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value
  }

  // Функция для отправки AJAX запроса
  async function sendAjaxRequest(url, data) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()
      return result
    } catch (error) {
      console.error("Error:", error)
      return { success: false, error: "Произошла ошибка при отправке запроса" }
    }
  }

  // Функция для показа уведомления
  function showNotification(message, isSuccess = true) {
    // Создаем простое уведомление
    const notification = document.createElement("div")
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background-color: ${isSuccess ? "#4CAF50" : "#f44336"};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            font-family: "GT Walsheim Pro", sans-serif;
        `
    notification.textContent = message
    document.body.appendChild(notification)

    setTimeout(() => {
      notification.remove()
    }, 3000)
  }

  function showModal(userData = null, action = null) {
    currentUserToDelete = userData
    currentAction = action
    modalOverlay.classList.add("active")
    document.body.style.overflow = "hidden"
  }

  function hideModal() {
    modalOverlay.classList.remove("active")
    document.body.style.overflow = "auto"
    currentUserToDelete = null
    currentAction = null
  }

  // Обработчики для кнопок удаления
  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault()

      const card = this.closest(".card")
      const userName = card.querySelector("h3").textContent
      const userHandle = card.querySelector("h4").textContent.replace("@", "")

      let action = "delete"
      if (this.classList.contains("delete-request")) {
        action = "decline-request"
      } else if (this.classList.contains("delete-recommendation")) {
        action = "remove-recommendation"
      } else if (this.classList.contains("delete-friend")) {
        action = "remove-friend"
      }

      currentUserToDelete = {
        name: userName,
        handle: userHandle,
        username: userHandle,
        element: card,
        button: this,
      }

      currentAction = action
      showModal(currentUserToDelete, action)
    })
  })

  // Обработчики для кнопок принятия запроса
  confirmButtons.forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault()

      const card = this.closest(".card")
      const userHandle = card.querySelector("h4").textContent.replace("@", "")

      const result = await sendAjaxRequest("/friends/accept-request/", {
        username: userHandle,
      })

      if (result.success) {
        // showNotification("Запрос на дружбу принят!")
        card.remove()

        // Обновляем страницу через небольшую задержку для лучшего UX
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        showNotification(result.error || "Произошла ошибка", false)
      }
    })
  })

  // Обработчики для кнопок добавления в друзья
  addButtons.forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault()

      const card = this.closest(".card")
      const userHandle = card.querySelector("h4").textContent.replace("@", "")

      const result = await sendAjaxRequest("/friends/send-request/", {
        username: userHandle,
      })

      if (result.success) {
        // showNotification("Запрос на дружбу отправлен!")
        card.remove()
      } else {
        showNotification(result.error || "Произошла ошибка", false)
      }
    })
  })

  // Обработчики модального окна
  closeBtn.addEventListener("click", hideModal)
  cancelBtn.addEventListener("click", (e) => {
    e.preventDefault()
    hideModal()
  })

  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      hideModal()
    }
  })

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modalOverlay.classList.contains("active")) {
      hideModal()
    }
  })

  // Обработчик подтверждения удаления
  confirmBtn.addEventListener("click", async (e) => {
    e.preventDefault()

    if (currentUserToDelete && currentAction) {
      let url = ""
      let successMessage = ""

      switch (currentAction) {
        case "decline-request":
          url = "/friends/decline-request/"
          successMessage = "Запрос отклонен"
          break
        case "remove-recommendation":
          url = "/friends/remove-recommendation/"
          successMessage = "Рекомендация удалена"
          break
        case "remove-friend":
          url = "/friends/remove-friend/"
          successMessage = "Друг удален"
          break
      }

      if (url) {
        const result = await sendAjaxRequest(url, {
          username: currentUserToDelete.username,
        })

        if (result.success) {
        //   showNotification(successMessage)
          currentUserToDelete.element.remove()

          // Для удаления друга обновляем страницу
          if (currentAction === "remove-friend") {
            setTimeout(() => {
              window.location.reload()
            }, 1000)
          }
        } else {
          showNotification(result.error || "Произошла ошибка", false)
        }
      }
    }

    hideModal()
  })
})
