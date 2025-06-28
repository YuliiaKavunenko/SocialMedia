document.addEventListener("DOMContentLoaded", () => {
  const chatPanel = document.getElementById("chat-panel")

  // поиск контактов
  const searchInput = document.getElementById("search")
  const contactsContainer = document.getElementById("contacts")

  if (searchInput && contactsContainer) {
    let searchTimeout

    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchTimeout)
      const query = e.target.value.trim()

      searchTimeout = setTimeout(() => {
        searchContacts(query)
      }, 300)
    })

    async function searchContacts(query) {
      try {
        const response = await fetch(`/chats/search-contacts/?q=${encodeURIComponent(query)}`)
        const data = await response.json()

        if (data.success) {
          displayContacts(data.contacts)
        }
      } catch (error) {
        console.error("Error searching contacts:", error)
      }
    }

    function displayContacts(contacts) {
      contactsContainer.innerHTML = ""

      contacts.forEach((contact) => {
        const contactLink = document.createElement("a")
        contactLink.href = `?contact_id=${contact.id}`
        contactLink.className = "contact-link"

        const contactDiv = document.createElement("div")
        contactDiv.className = "contact"

        const img = document.createElement("img")
        img.src = contact.avatar || "/static/img/avatarka.png"
        img.className = "user-photo"
        img.alt = contact.username

        const h4 = document.createElement("h4")
        h4.textContent = contact.name

        contactDiv.appendChild(img)
        contactDiv.appendChild(h4)
        contactLink.appendChild(contactDiv)
        contactsContainer.appendChild(contactLink)
      })
    }
  }

  if (chatPanel) {
    const currentUserId = Number.parseInt(chatPanel.dataset.userId)
    const chatId = chatPanel.dataset.chatId
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws"

    const chatSocket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/chat/${chatId}/`)

    let lastMessageDate = null

    chatSocket.onopen = (e) => {
      console.log("WebSocket connection established")
    }

    chatSocket.onclose = (e) => {
      console.log("WebSocket connection closed")
    }

    chatSocket.onerror = (e) => {
      console.error("WebSocket error:", e)
    }

    chatSocket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)

        if (data.type === "message") {
          handleNewMessage(data)
        } else if (data.type === "chat_list_update") {
          updateChatList(data)
        }
      } catch (error) {
        console.error("Error parsing message:", error)
      }
    }

    function handleNewMessage(data) {
      const chatMessages = document.getElementById("chat-messages")

      if (lastMessageDate !== data.date) {
        const dateContainer = document.createElement("div")
        dateContainer.classList.add("date-container")

        const dateDiv = document.createElement("div")
        dateDiv.classList.add("message-date")
        const dateObj = new Date(data.date)
        const options = {
          year: "numeric",
          month: "long",
          day: "numeric",
          weekday: "long",
        }
        dateDiv.textContent = dateObj.toLocaleDateString("uk-UA", options)

        dateContainer.appendChild(dateDiv)
        chatMessages.appendChild(dateContainer)
        lastMessageDate = data.date
      }

      const msg = document.createElement("div")
      msg.classList.add("message")
      msg.classList.add(data.author_id === currentUserId ? "sent" : "received")

      const avatar = document.createElement("img")
      avatar.src = data.author_avatar
      avatar.alt = data.author_name
      avatar.classList.add("message-avatar")
      msg.appendChild(avatar)

      const messageContent = document.createElement("div")
      messageContent.classList.add("message-content")

      const imageAndTextDiv = document.createElement("div")
      imageAndTextDiv.classList.add("image-and-text")

      if (data.message_type === "image" && data.image_url) {
        const img = document.createElement("img")
        img.src = data.image_url
        img.alt = "Зображення"
        img.classList.add("message-image")
        imageAndTextDiv.appendChild(img)
      }

      if (data.message) {
        const p = document.createElement("p")
        p.innerText = data.message
        imageAndTextDiv.appendChild(p)
      }

      messageContent.appendChild(imageAndTextDiv)

      const messageTimeContainer = document.createElement("div")
      messageTimeContainer.classList.add("message-time-container")

      const time = document.createElement("span")
      time.classList.add("message-time")
      time.innerText = data.sent_at
      messageTimeContainer.appendChild(time)

      messageContent.appendChild(messageTimeContainer)
      msg.appendChild(messageContent)
      chatMessages.appendChild(msg)
      chatMessages.scrollTop = chatMessages.scrollHeight
    }

    function updateChatList(data) {
      const chatsList = document.getElementById("chats")
      const groupsList = document.getElementById("groups")
      const targetList = data.is_personal ? chatsList : groupsList

      if (!targetList) return

      const existingChat = targetList.querySelector(`a[href*="chat_id=${data.chat_id}"]`)

      if (existingChat) {
        const timeElement = existingChat.querySelector(".user h5, .info h5")
        const messageElement = existingChat.querySelector(".chat-info > h5, .group-info > h5")
        const avatarElement = existingChat.querySelector(".chat-avatar, .group img")

        if (timeElement) timeElement.textContent = data.last_message_time
        if (messageElement)
          messageElement.textContent =
            data.last_message.length > 30 ? data.last_message.substring(0, 30) + "..." : data.last_message

        // аватарка для персональных чатов
        if (data.is_personal && avatarElement && data.other_member_avatar) {
          avatarElement.src = data.other_member_avatar
        }

        targetList.insertBefore(existingChat, targetList.firstChild)
      } else {
        const newChatLink = document.createElement("a")
        newChatLink.href = `?chat_id=${data.chat_id}`

        const newChatDiv = document.createElement("div")
        newChatDiv.classList.add(data.is_personal ? "chat" : "group")

        if (data.is_personal) {
          newChatDiv.innerHTML = `
            <img src="${data.other_member_avatar || "/static/img/avatarka.png"}" alt="${data.chat_name}" class="chat-avatar">
            <div class="chat-info">
              <div class="user">
                <h4>${data.chat_name}</h4>
                <h5>${data.last_message_time}</h5>
              </div>
              <h5>${data.last_message.length > 30 ? data.last_message.substring(0, 30) + "..." : data.last_message}</h5>
            </div>
          `
        } else {
          newChatDiv.innerHTML = `
            <img src="/placeholder.svg?height=40&width=40" alt="${data.chat_name}">
            <div class="group-info">
              <div class="info">
                <h4>${data.chat_name}</h4>
                <h5>${data.last_message_time}</h5>
              </div>
              <h5>${data.last_message.length > 30 ? data.last_message.substring(0, 30) + "..." : data.last_message}</h5>
            </div>
          `
        }

        newChatLink.appendChild(newChatDiv)
        targetList.insertBefore(newChatLink, targetList.firstChild)
      }
    }

    const messageForm = document.querySelector("#message-form")
    const messageInput = messageForm.querySelector("textarea[name='content']")
    const sendButton = document.querySelector("#send-message")
    const sendImageButton = document.querySelector("#send-image")
    const fileInput = document.querySelector("#hidden-file-input")

    const modal = document.getElementById("image-modal")
    const modalImage = document.getElementById("modal-image")
    const captionInput = document.getElementById("image-caption")
    const closeModal = document.getElementById("close-modal")
    const sendImageModal = document.getElementById("send-image-modal")

    const backButton = document.getElementById("back-button")
    const menuButton = document.getElementById("menu-button")
    const dropdownMenu = document.getElementById("chat-dropdown-menu")
    const viewMediaOption = document.getElementById("view-media-option")
    const deleteChatOption = document.getElementById("delete-chat-option")
    const leaveGroupOption = document.getElementById("leave-group-option")
    const editGroupOption = document.getElementById("edit-group-option")
    const deleteConfirmModal = document.getElementById("delete-confirm-modal")
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn")
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn")

    messageInput.focus()

    const existingMessages = document.querySelectorAll(".message")
    if (existingMessages.length > 0) {
      const today = new Date().toISOString().split("T")[0]
      lastMessageDate = today
    }

    function sendMessage(e) {
      e.preventDefault()
      const message = messageInput.value.trim()

      if (message.length > 0 && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(
          JSON.stringify({
            type: "text",
            message: message,
          }),
        )
        messageInput.value = ""
        messageInput.focus()
      }
    }

    function sendImage(imageData, caption) {
      if (chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(
          JSON.stringify({
            type: "image",
            image: imageData,
            caption: caption,
          }),
        )
      }
    }

    function showImageModal(imageData) {
      modalImage.src = imageData
      captionInput.value = ""
      modal.style.display = "flex"
      captionInput.focus()
      modal.dataset.imageData = imageData
    }

    function goBackToEmptyPanel() {
      window.location.href = window.location.pathname
    }

    function toggleDropdownMenu() {
      const isVisible = dropdownMenu.style.display === "block"
      if (isVisible) {
        dropdownMenu.style.display = "none"
      } else {
        dropdownMenu.style.display = "block"
      }
    }

    function hideDropdownMenu() {
      dropdownMenu.style.display = "none"
    }

    function showDeleteConfirm() {
      hideDropdownMenu()
      deleteConfirmModal.style.display = "flex"
    }

    function hideDeleteConfirm() {
      deleteConfirmModal.style.display = "none"
    }

    async function deleteOrLeaveChat() {
      try {
        const response = await fetch(`/chats/delete/${chatId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            hideDeleteConfirm()
            window.location.href = window.location.pathname
          } else {
            console.log("Помилка: " + data.error)
          }
        } else {
          console.log("Помилка при виконанні операції")
        }
      } catch (error) {
        console.error("Error:", error)
        console.log("Помилка при виконанні операції")
      }
    }

    function viewMedia() {
      console.log("Viewing media for chat ID:", chatId)
      hideDropdownMenu()
    }

    const editGroupModal = document.getElementById("edit-group-modal")
    const closeEditGroup = document.getElementById("close-edit-group")
    const cancelEditGroup = document.getElementById("cancel-edit-group")
    const saveGroupChangesBtn = document.getElementById("save-group-changes")
    const editGroupNameInput = document.getElementById("edit-group-name-input")
    const editAvatarPreview = document.getElementById("edit-avatar-preview")
    const editAvatarInitials = document.getElementById("edit-avatar-initials")
    const editAvatarImage = document.getElementById("edit-avatar-image")
    const editAddAvatarBtn = document.getElementById("edit-add-avatar-btn")
    const editChooseAvatarBtn = document.getElementById("edit-choose-avatar-btn")
    const editGroupAvatarInput = document.getElementById("edit-group-avatar-input")
    const editParticipantsList = document.getElementById("edit-participants-list")
    const addParticipantBtn = document.getElementById("add-participant-btn")

    const addParticipantsModal = document.getElementById("add-participants-modal")
    const closeAddParticipants = document.getElementById("close-add-participants")
    const cancelAddParticipants = document.getElementById("cancel-add-participants")
    const saveAddParticipants = document.getElementById("save-add-participants")
    const addParticipantsSearch = document.getElementById("add-participants-search")
    const addParticipantsList = document.getElementById("add-participants-list")
    const addParticipantsCountText = document.getElementById("add-participants-count-text")

    let currentGroupData = null
    let editGroupAvatarFile = null
    let selectedNewParticipants = []
    let availableUsers = []

    async function showEditGroupModal() {
      if (!chatPanel) return

      const chatId = chatPanel.dataset.chatId

      try {
        const response = await fetch(`/chats/get-group-data/${chatId}/`)
        const data = await response.json()

        if (data.success) {
          currentGroupData = data.group

          // Заполняем форму текущими данными
          editGroupNameInput.value = currentGroupData.name

          // Устанавливаем аватар
          if (currentGroupData.avatar) {
            editAvatarImage.src = currentGroupData.avatar
            editAvatarImage.style.display = "block"
            editAvatarInitials.style.display = "none"
          } else {
            updateEditAvatarInitials()
            editAvatarImage.style.display = "none"
            editAvatarInitials.style.display = "block"
          }

          // Отображаем участников
          displayEditParticipants()

          editGroupModal.style.display = "flex"
          hideDropdownMenu()
        }
      } catch (error) {
        console.error("Error loading group data:", error)
        console.log("Помилка при завантаженні даних групи")
      }
    }

    function displayEditParticipants() {
      editParticipantsList.innerHTML = ""

      currentGroupData.members.forEach((member) => {
        const participantItem = document.createElement("div")
        participantItem.className = "participant-item"

        // Не показываем кнопку удаления для администратора
        const isAdmin = member.id === currentGroupData.admin_id

        participantItem.innerHTML = `
      <div class="participant-info">
        <img src="${member.avatar || "/static/img/avatarka.png"}" alt="${member.name}" class="participant-avatar">
        <span class="participant-name">${member.name}${isAdmin ? " (Адмін)" : ""}</span>
      </div>
      ${
        !isAdmin
          ? `
        <button class="remove-participant" data-user-id="${member.id}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
          </svg>
        </button>
      `
          : ""
      }
    `

        editParticipantsList.appendChild(participantItem)

        if (!isAdmin) {
          const removeBtn = participantItem.querySelector(".remove-participant")
          removeBtn.addEventListener("click", () => removeParticipant(member.id))
        }
      })
    }

    async function removeParticipant(memberId) {
      if (!confirm("Ви впевнені, що хочете видалити цього учасника з групи?")) {
        return
      }

      const chatId = chatPanel.dataset.chatId

      try {
        const response = await fetch(`/chats/remove-member/${chatId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
          body: JSON.stringify({ member_id: memberId }),
        })

        const data = await response.json()
        if (data.success) {
          // Обновляем список участников
          currentGroupData.members = currentGroupData.members.filter((m) => m.id !== memberId)
          displayEditParticipants()
        } else {
          console.log("Помилка при видаленні учасника: " + data.error)
        }
      } catch (error) {
        console.error("Error removing participant:", error)
        console.log("Помилка при видаленні учасника")
      }
    }

    async function showAddParticipantsModal() {
      try {
        const response = await fetch("/chats/get-users/")
        const data = await response.json()

        if (data.success) {
          // Фильтруем пользователей, которые уже в группе
          const currentMemberIds = currentGroupData.members.map((m) => m.id)
          availableUsers = data.users.filter((user) => !currentMemberIds.includes(user.id))

          displayAvailableUsers(availableUsers)
          selectedNewParticipants = []
          updateAddParticipantsCount()
          updateAddParticipantsButton()

          editGroupModal.style.display = "none"
          addParticipantsModal.style.display = "flex"
        }
      } catch (error) {
        console.error("Error loading users:", error)
        console.log("Помилка при завантаженні користувачів")
      }
    }

    function displayAvailableUsers(users) {
      addParticipantsList.innerHTML = ""

      // Группируем пользователей по первой букве
      const groupedUsers = {}
      users.forEach((user) => {
        const firstLetter = user.name[0].toUpperCase()
        if (!groupedUsers[firstLetter]) {
          groupedUsers[firstLetter] = []
        }
        groupedUsers[firstLetter].push(user)
      })

      // Сортируем группы по алфавиту
      const sortedGroups = Object.keys(groupedUsers).sort()

      sortedGroups.forEach((letter) => {
        // Добавляем заголовок группы
        const groupHeader = document.createElement("div")
        groupHeader.className = "users-group-header"
        groupHeader.textContent = letter
        addParticipantsList.appendChild(groupHeader)

        // Добавляем пользователей группы
        groupedUsers[letter].forEach((user) => {
          const userItem = document.createElement("div")
          userItem.className = "user-item"
          userItem.innerHTML = `
        <div class="user-info">
          <img src="${user.avatar || "/static/img/avatarka.png"}" alt="${user.name}" class="user-avatar">
          <span class="user-name">${user.name}</span>
        </div>
        <div class="user-checkbox">
          <input type="checkbox" id="add-user-${user.id}" data-user-id="${user.id}">
          <label for="add-user-${user.id}"></label>
        </div>
      `
          addParticipantsList.appendChild(userItem)

          const checkbox = userItem.querySelector('input[type="checkbox"]')
          checkbox.addEventListener("change", (e) => {
            if (e.target.checked) {
              selectedNewParticipants.push(user)
            } else {
              selectedNewParticipants = selectedNewParticipants.filter((u) => u.id !== user.id)
            }
            updateAddParticipantsCount()
            updateAddParticipantsButton()
          })
        })
      })
    }

    function updateAddParticipantsCount() {
      addParticipantsCountText.textContent = `Вибрано: ${selectedNewParticipants.length}`
    }

    function updateAddParticipantsButton() {
      saveAddParticipants.disabled = selectedNewParticipants.length === 0
    }

    async function saveNewParticipants() {
      if (selectedNewParticipants.length === 0) return

      const chatId = chatPanel.dataset.chatId

      try {
        const response = await fetch(`/chats/add-members/${chatId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
          body: JSON.stringify({
            member_ids: selectedNewParticipants.map((u) => u.id),
          }),
        })

        const data = await response.json()
        if (data.success) {
          // Обновляем данные группы
          currentGroupData.members = [...currentGroupData.members, ...selectedNewParticipants]
          displayEditParticipants()

          addParticipantsModal.style.display = "none"
          editGroupModal.style.display = "flex"
        } else {
          console.log("Помилка при додаванні учасників: " + data.error)
        }
      } catch (error) {
        console.error("Error adding participants:", error)
        console.log("Помилка при додаванні учасників")
      }
    }

    function updateEditAvatarInitials() {
      const name = editGroupNameInput.value.trim()
      if (name) {
        const words = name.split(" ")
        const initials = words.length > 1 ? words[0][0] + words[1][0] : words[0][0] + (words[0][1] || "")
        editAvatarInitials.textContent = initials.toUpperCase()
      } else if (currentGroupData) {
        const words = currentGroupData.name.split(" ")
        const initials = words.length > 1 ? words[0][0] + words[1][0] : words[0][0] + (words[0][1] || "")
        editAvatarInitials.textContent = initials.toUpperCase()
      }
    }

    async function saveGroupChanges() {
      const groupName = editGroupNameInput.value.trim()
      if (!groupName) {
        console.log("Введіть назву групи")
        return
      }

      const chatId = chatPanel.dataset.chatId
      const formData = new FormData()
      formData.append("name", groupName)

      if (editGroupAvatarFile) {
        formData.append("avatar", editGroupAvatarFile)
      }

      try {
        const response = await fetch(`/chats/update-group/${chatId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
          body: formData,
        })

        const data = await response.json()
        if (data.success) {
          editGroupModal.style.display = "none"
          // Обновляем название в заголовке чата
          document.querySelector("#chat-title h4").textContent = groupName
        } else {
          console.log("Помилка при збереженні змін: " + data.error)
        }
      } catch (error) {
        console.error("Error saving group changes:", error)
        console.log("Помилка при збереженні змін")
      }
    }

    async function leaveGroup() {
      if (!confirm("Ви впевнені, що хочете покинути цю групу?")) {
        return
      }

      const chatId = chatPanel.dataset.chatId

      try {
        const response = await fetch(`/chats/leave-group/${chatId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
        })

        const data = await response.json()
        if (data.success) {
          window.location.href = window.location.pathname
        } else {
          console.log("Помилка при виході з групи: " + data.error)
        }
      } catch (error) {
        console.error("Error leaving group:", error)
        console.log("Помилка при виході з групи")
      }
    }

    if (backButton) {
      backButton.addEventListener("click", goBackToEmptyPanel)
    }

    if (menuButton) {
      menuButton.addEventListener("click", (e) => {
        e.stopPropagation()
        toggleDropdownMenu()
      })
    }

    if (viewMediaOption) {
      viewMediaOption.addEventListener("click", viewMedia)
    }

    if (deleteChatOption) {
      deleteChatOption.addEventListener("click", showDeleteConfirm)
    }

    if (leaveGroupOption) {
      leaveGroupOption.addEventListener("click", showDeleteConfirm)
    }

    if (editGroupOption) {
      editGroupOption.addEventListener("click", showEditGroupModal)
    }

    if (cancelDeleteBtn) {
      cancelDeleteBtn.addEventListener("click", hideDeleteConfirm)
    }

    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener("click", deleteOrLeaveChat)
    }

    if (closeEditGroup) {
      closeEditGroup.addEventListener("click", () => {
        editGroupModal.style.display = "none"
      })
    }

    if (cancelEditGroup) {
      cancelEditGroup.addEventListener("click", () => {
        editGroupModal.style.display = "none"
      })
    }

    if (saveGroupChangesBtn) {
      saveGroupChangesBtn.addEventListener("click", saveGroupChanges)
    }

    if (addParticipantBtn) {
      addParticipantBtn.addEventListener("click", showAddParticipantsModal)
    }

    if (editGroupNameInput) {
      editGroupNameInput.addEventListener("input", updateEditAvatarInitials)
    }

    if (editAddAvatarBtn || editChooseAvatarBtn) {
      ;[editAddAvatarBtn, editChooseAvatarBtn].forEach((btn) => {
        if (btn) {
          btn.addEventListener("click", () => {
            editGroupAvatarInput.click()
          })
        }
      })
    }

    if (editGroupAvatarInput) {
      editGroupAvatarInput.addEventListener("change", (e) => {
        const file = e.target.files[0]
        if (file && file.type.startsWith("image/")) {
          editGroupAvatarFile = file
          const reader = new FileReader()
          reader.onload = (e) => {
            editAvatarImage.src = e.target.result
            editAvatarImage.style.display = "block"
            editAvatarInitials.style.display = "none"
          }
          reader.readAsDataURL(file)
        }
      })
    }

    if (closeAddParticipants) {
      closeAddParticipants.addEventListener("click", () => {
        addParticipantsModal.style.display = "none"
        editGroupModal.style.display = "flex"
      })
    }

    if (cancelAddParticipants) {
      cancelAddParticipants.addEventListener("click", () => {
        addParticipantsModal.style.display = "none"
        editGroupModal.style.display = "flex"
      })
    }

    if (saveAddParticipants) {
      saveAddParticipants.addEventListener("click", saveNewParticipants)
    }

    if (addParticipantsSearch) {
      addParticipantsSearch.addEventListener("input", (e) => {
        const searchTerm = e.target.value.toLowerCase()
        const filteredUsers = availableUsers.filter((user) => user.name.toLowerCase().includes(searchTerm))
        displayAvailableUsers(filteredUsers)

        selectedNewParticipants.forEach((selectedUser) => {
          const checkbox = document.querySelector(`#add-user-${selectedUser.id}`)
          if (checkbox) {
            checkbox.checked = true
          }
        })
      })
    }

    document.addEventListener("click", (e) => {
      if (menuButton && dropdownMenu && !menuButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
        hideDropdownMenu()
      }
    })
    ;[editGroupModal, addParticipantsModal].forEach((modal) => {
      if (modal) {
        modal.addEventListener("click", (e) => {
          if (e.target === modal) {
            modal.style.display = "none"
          }
        })
      }
    })

    if (deleteConfirmModal) {
      deleteConfirmModal.addEventListener("click", (e) => {
        if (e.target === deleteConfirmModal) {
          hideDeleteConfirm()
        }
      })
    }

    if (sendButton) {
      sendButton.addEventListener("click", sendMessage)
    }

    if (sendImageButton) {
      sendImageButton.addEventListener("click", (e) => {
        e.preventDefault()
        if (fileInput) {
          fileInput.click()
        }
      })
    }

    if (fileInput) {
      fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0]

        if (file && file.type.startsWith("image/")) {
          const reader = new FileReader()
          reader.onload = (e) => {
            showImageModal(e.target.result)
          }
          reader.readAsDataURL(file)
        }
        fileInput.value = ""
      })
    }

    if (closeModal) {
      closeModal.addEventListener("click", () => {
        modal.style.display = "none"
      })
    }

    if (sendImageModal) {
      sendImageModal.addEventListener("click", () => {
        const imageData = modal.dataset.imageData
        const caption = captionInput.value.trim()

        if (imageData) {
          sendImage(imageData, caption)
          modal.style.display = "none"
        }
      })
    }

    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          modal.style.display = "none"
        }
      })
    }

    if (captionInput) {
      captionInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault()
          sendImageModal.click()
        }
      })
    }

    messageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        sendMessage(e)
      }
    })

    messageForm.addEventListener("submit", (e) => {
      e.preventDefault()
      sendMessage(e)
    })

    const chatMessages = document.getElementById("chat-messages")

    if (chatMessages) {
      scrollToBottom()

      function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight
      }

      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
            scrollToBottom()
          }
        })
      })

      observer.observe(chatMessages, {
        childList: true,
        subtree: true,
      })
    }
  }

  const createGroupBtn = document.getElementById("create-group")
  const createGroupModalStep1 = document.getElementById("create-group-modal-step1")
  const createGroupModalStep2 = document.getElementById("create-group-modal-step2")
  const closeCreateGroupStep1 = document.getElementById("close-create-group-step1")
  const closeCreateGroupStep2 = document.getElementById("close-create-group-step2")
  const cancelCreateGroupStep1 = document.getElementById("cancel-create-group-step1")
  const nextCreateGroupStep1 = document.getElementById("next-create-group-step1")
  const backCreateGroupStep2 = document.getElementById("back-create-group-step2")
  const createGroupFinal = document.getElementById("create-group-final")
  const groupUserSearch = document.getElementById("group-user-search")
  const usersList = document.getElementById("users-list")
  const selectedCountText = document.getElementById("selected-count-text")
  const participantsList = document.getElementById("participants-list")
  const groupNameInput = document.getElementById("group-name-input")
  const avatarPreview = document.getElementById("avatar-preview")
  const avatarInitials = document.getElementById("avatar-initials")
  const avatarImage = document.getElementById("avatar-image")
  const addAvatarBtn = document.getElementById("add-avatar-btn")
  const chooseAvatarBtn = document.getElementById("choose-avatar-btn")
  const groupAvatarInput = document.getElementById("group-avatar-input")

  let selectedUsers = []
  let allUsers = []
  let groupAvatarFile = null

  async function loadUsers() {
    try {
      const response = await fetch("/chats/get-users/")
      const data = await response.json()
      allUsers = data.users
      displayUsers(allUsers)
    } catch (error) {
      console.error("Error loading users:", error)
    }
  }

  function displayUsers(users) {
    usersList.innerHTML = ""
    users.forEach((user) => {
      const userItem = document.createElement("div")
      userItem.className = "user-item"
      userItem.innerHTML = `
      <div class="user-info">
        <img src="${user.avatar || "/static/img/avatarka.png"}" alt="${user.name}" class="user-avatar">
        <span class="user-name">${user.name}</span>
      </div>
      <div class="user-checkbox">
        <input type="checkbox" id="user-${user.id}" data-user-id="${user.id}">
        <label for="user-${user.id}"></label>
      </div>
    `
      usersList.appendChild(userItem)

      const checkbox = userItem.querySelector('input[type="checkbox"]')
      checkbox.addEventListener("change", (e) => {
        if (e.target.checked) {
          selectedUsers.push(user)
        } else {
          selectedUsers = selectedUsers.filter((u) => u.id !== user.id)
        }
        updateSelectedCount()
        updateNextButton()
      })
    })
  }

  function updateSelectedCount() {
    selectedCountText.textContent = `Вибрано: ${selectedUsers.length}`
  }

  function updateNextButton() {
    nextCreateGroupStep1.disabled = selectedUsers.length === 0
  }

  function displayParticipants() {
    participantsList.innerHTML = ""
    selectedUsers.forEach((user) => {
      const participantItem = document.createElement("div")
      participantItem.className = "participant-item"
      participantItem.innerHTML = `
      <div class="participant-info">
        <img src="${user.avatar || "/static/img/avatarka.png"}" alt="${user.name}" class="participant-avatar">
        <span class="participant-name">${user.name}</span>
      </div>
      <button class="remove-participant" data-user-id="${user.id}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
        </svg>
      </button>
    `
      participantsList.appendChild(participantItem)

      const removeBtn = participantItem.querySelector(".remove-participant")
      removeBtn.addEventListener("click", () => {
        selectedUsers = selectedUsers.filter((u) => u.id !== Number.parseInt(removeBtn.dataset.userId))
        displayParticipants()

        const checkbox = document.querySelector(`#user-${removeBtn.dataset.userId}`)
        if (checkbox) {
          checkbox.checked = false
        }
        updateSelectedCount()
        updateNextButton()
      })
    })
  }

  function updateAvatarInitials() {
    const name = groupNameInput.value.trim()
    if (name) {
      const words = name.split(" ")
      const initials = words.length > 1 ? words[0][0] + words[1][0] : words[0][0] + (words[0][1] || "")
      avatarInitials.textContent = initials.toUpperCase()
    } else {
      avatarInitials.textContent = ""
    }
  }

  async function createGroup() {
    const groupName = groupNameInput.value.trim()
    if (!groupName) {
      
      return
    }

    if (selectedUsers.length === 0) {
     
      return
    }

    const formData = new FormData()
    formData.append("name", groupName)
    formData.append("members", JSON.stringify(selectedUsers.map((u) => u.id)))

    if (groupAvatarFile) {
      formData.append("avatar", groupAvatarFile)
    }

    try {
      const response = await fetch("/chats/create-group/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: formData,
      })

      const data = await response.json()
      if (data.success) {
        hideCreateGroupModals()
        window.location.href = `?chat_id=${data.chat_id}`
      } else {
        console.log("Помилка при створенні групи: " + data.error)
      }
    } catch (error) {
      console.error("Error creating group:", error)
      console.log("Помилка при створенні групи")
    }
  }

  function showCreateGroupStep1() {
    createGroupModalStep1.style.display = "flex"
    loadUsers()
  }

  function hideCreateGroupModals() {
    createGroupModalStep1.style.display = "none"
    createGroupModalStep2.style.display = "none"

    selectedUsers = []
    groupAvatarFile = null
    groupNameInput.value = ""
    avatarImage.style.display = "none"
    avatarInitials.style.display = "block"
    avatarInitials.textContent = "NG"
    updateSelectedCount()
    updateNextButton()
  }

  function showCreateGroupStep2() {
    createGroupModalStep1.style.display = "none"
    createGroupModalStep2.style.display = "flex"
    displayParticipants()
    updateAvatarInitials()
  }

  function showCreateGroupStep1FromStep2() {
    createGroupModalStep2.style.display = "none"
    createGroupModalStep1.style.display = "flex"
  }

  if (createGroupBtn) {
    createGroupBtn.addEventListener("click", showCreateGroupStep1)
  }

  if (closeCreateGroupStep1) {
    closeCreateGroupStep1.addEventListener("click", hideCreateGroupModals)
  }

  if (closeCreateGroupStep2) {
    closeCreateGroupStep2.addEventListener("click", hideCreateGroupModals)
  }

  if (cancelCreateGroupStep1) {
    cancelCreateGroupStep1.addEventListener("click", hideCreateGroupModals)
  }

  if (nextCreateGroupStep1) {
    nextCreateGroupStep1.addEventListener("click", showCreateGroupStep2)
  }

  if (backCreateGroupStep2) {
    backCreateGroupStep2.addEventListener("click", showCreateGroupStep1FromStep2)
  }

  if (createGroupFinal) {
    createGroupFinal.addEventListener("click", createGroup)
  }

  if (groupUserSearch) {
    groupUserSearch.addEventListener("input", (e) => {
      const searchTerm = e.target.value.toLowerCase()
      const filteredUsers = allUsers.filter((user) => user.name.toLowerCase().includes(searchTerm))
      displayUsers(filteredUsers)

      selectedUsers.forEach((selectedUser) => {
        const checkbox = document.querySelector(`#user-${selectedUser.id}`)
        if (checkbox) {
          checkbox.checked = true
        }
      })
    })
  }

  if (groupNameInput) {
    groupNameInput.addEventListener("input", updateAvatarInitials)
  }

  if (addAvatarBtn || chooseAvatarBtn) {
    ;[addAvatarBtn, chooseAvatarBtn].forEach((btn) => {
      if (btn) {
        btn.addEventListener("click", () => {
          groupAvatarInput.click()
        })
      }
    })
  }

  if (groupAvatarInput) {
    groupAvatarInput.addEventListener("change", (e) => {
      const file = e.target.files[0]
      if (file && file.type.startsWith("image/")) {
        groupAvatarFile = file
        const reader = new FileReader()
        reader.onload = (e) => {
          avatarImage.src = e.target.result
          avatarImage.style.display = "block"
          avatarInitials.style.display = "none"
        }
        reader.readAsDataURL(file)
      }
    })
  }
  ;[createGroupModalStep1, createGroupModalStep2].forEach((modal) => {
    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          hideCreateGroupModals()
        }
      })
    }
  })
})
