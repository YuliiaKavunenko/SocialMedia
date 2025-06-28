document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("delete-user-modal")
  const modalOverlay = document.querySelector(".modal-overlay")
  const closeBtn = document.querySelector(".modal-close")
  const cancelBtn = document.querySelector(".cancel-delete-user")
  const confirmBtn = document.querySelector(".confirm-delete-user")

  const deleteButtons = document.querySelectorAll(".delete-request, .delete-recommendation, .delete-friend")
  const confirmButtons = document.querySelectorAll(".confirm-request")
  const addButtons = document.querySelectorAll(".add-recommendation")
  const messageButtons = document.querySelectorAll(".message-friend")

  let currentUserToDelete = null
  let currentAction = null

  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value
  }

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

  messageButtons.forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault()

      const card = this.closest(".card")
      const userHandle = card.querySelector("h4").textContent.replace("@", "")

      try {
        const result = await sendAjaxRequest("/friends/create-personal-chat/", {
          username: userHandle,
        })

        if (result.success) {
          window.location.href = `/chats/chats/?chat_id=${result.chat_id}`
        } else {
          console.log(result.error || "Произошла ошибка при создании чата")
        }
      } catch (error) {
        console.error("Error:", error)
        console.log("Произошла ошибка при создании чата")
      }
    })
  })

  document.addEventListener("click", (e) => {
    const target = e.target

    if ((target.tagName === "H3" || target.tagName === "H4") && target.textContent.includes("@")) {
      const username = target.textContent.replace("@", "")
      window.location.href = `/friends/user/${username}/`
    } else if (target.tagName === "H3" && target.closest(".card")) {
      const card = target.closest(".card")
      const nicknameElement = card.querySelector("h4")
      if (nicknameElement && nicknameElement.textContent.includes("@")) {
        const username = nicknameElement.textContent.replace("@", "")
        window.location.href = `/friends/user/${username}/`
      }
    }
  })

  const userNames = document.querySelectorAll(".card h3, .card h4")
  userNames.forEach((element) => {
    element.style.cursor = "pointer"

  })

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

  confirmButtons.forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault()

      const card = this.closest(".card")
      const userHandle = card.querySelector("h4").textContent.replace("@", "")

      const result = await sendAjaxRequest("/friends/accept-request/", {
        username: userHandle,
      })

      if (result.success) {
        card.remove()

        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        console.log(result.error || "Произошла ошибка")
      }
    })
  })

  addButtons.forEach((button) => {
    button.addEventListener("click", async function (e) {
      e.preventDefault()

      const card = this.closest(".card")
      const userHandle = card.querySelector("h4").textContent.replace("@", "")

      const result = await sendAjaxRequest("/friends/send-request/", {
        username: userHandle,
      })

      if (result.success) {
        card.remove()
      } else {
        console.log(result.error || "Произошла ошибка")
      }
    })
  })

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
          currentUserToDelete.element.remove()

          if (currentAction === "remove-friend") {
            setTimeout(() => {
              window.location.reload()
            }, 1000)
          }
        } else {
          console.log(result.error || "Произошла ошибка")
        }
      }
    }

    hideModal()
  })
})
