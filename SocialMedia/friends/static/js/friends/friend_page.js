document.addEventListener("DOMContentLoaded", () => {
  function getCSRFToken() {
    return (
      document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
      document.querySelector('meta[name="csrf-token"]')?.getAttribute("content")
    )
  }

  async function sendRequest(url, data) {
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

  const username = window.profileUsername

  if (!username) {
    console.error("Username не найден!")
    return
  }

  const messageBtn = document.getElementById("message-user")
  if (messageBtn) {
    messageBtn.addEventListener("click", async (e) => {
      e.preventDefault()

      const result = await sendRequest("/friends/create-personal-chat/", { username: username })

      if (result.success) {
        window.location.href = `/chats/chats/?chat_id=${result.chat_id}`;
      } else {
        alert(result.error || "Произошла ошибка при создании чата")
      }
    })
  }

  const sendRequestBtn = document.getElementById("send-request")
  if (sendRequestBtn) {
    sendRequestBtn.addEventListener("click", async (e) => {
      e.preventDefault()

      const result = await sendRequest("/friends/send-request/", { username: username })

      if (result.success) {
        location.reload()
      } else {
        alert(result.error || "Произошла ошибка")
      }
    })
  }

  const acceptRequestBtn = document.getElementById("accept-request")
  if (acceptRequestBtn) {
    acceptRequestBtn.addEventListener("click", async (e) => {
      e.preventDefault()

      const result = await sendRequest("/friends/accept-request/", { username: username })

      if (result.success) {
        location.reload()
      } else {
        alert(result.error || "Произошла ошибка")
      }
    })
  }

  const declineRequestBtn = document.getElementById("decline-request")
  if (declineRequestBtn) {
    declineRequestBtn.addEventListener("click", async (e) => {
      e.preventDefault()

      const result = await sendRequest("/friends/decline-request/", { username: username })

      if (result.success) {
        location.reload()
      } else {
        alert(result.error || "Произошла ошибка")
      }
    })
  }

  const removeFriendBtn = document.getElementById("remove-friend")
  if (removeFriendBtn) {
    removeFriendBtn.addEventListener("click", async (e) => {
      e.preventDefault()

      if (confirm("Вы уверены, что хотите удалить этого пользователя из друзей?")) {
        const result = await sendRequest("/friends/remove-friend/", { username: username })

        if (result.success) {
          location.reload()
        } else {
          alert(result.error || "Произошла ошибка")
        }
      }
    })
  }
})
