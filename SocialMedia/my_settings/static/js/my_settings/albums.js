document.addEventListener("DOMContentLoaded", () => {
  const createAlbum = document.getElementById("create-albums")
  const albumForm = document.getElementById("create-album-window-background")
  const editForm = document.getElementById("edit-album-window-background")

  createAlbum.addEventListener("click", (event) => {
    event.preventDefault()
    albumForm.style.display = "block"
  })
  const closeButton = document.getElementById("close-button")
  if (closeButton) {
    closeButton.addEventListener("click", (event) => {
      event.preventDefault()
      albumForm.style.display = "none"
    })
  }

  // при натисканні на кнопку відкриваємо вибір файлу
  document.querySelectorAll(".add-photo-button").forEach((button) => {
    button.addEventListener("click", function () {
      const albumId = this.dataset.albumId
      const input = document.querySelector(`.photo-input[data-album-id="${albumId}"]`)
      input.click() // відкриває вікно вибору
    })
  })

  // коли користувач обрав файл
  document.querySelectorAll(".photo-input").forEach((input) => {
    input.addEventListener("change", function () {
      const albumId = this.dataset.albumId
      const file = this.files[0]

      if (!file) return

      const formData = new FormData()
      formData.append("album_id", albumId)
      formData.append("file", file)

      fetch("/ajax/upload-photo/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            const container = document.getElementById(`photo-list-${albumId}`) || this.closest(".photo-list")

            // Создаем контейнер для фото с кнопкой удаления
            const photoContainer = document.createElement("div")
            photoContainer.className = "album-photo-container"

            const img = document.createElement("img")
            img.src = data.image_url
            img.alt = data.filename

            const deleteBtn = document.createElement("button")
            deleteBtn.type = "button"
            deleteBtn.className = "delete-album-photo-btn"
            deleteBtn.dataset.imageId = data.image_id
            deleteBtn.dataset.albumId = albumId
            deleteBtn.textContent = "🗑"

            photoContainer.appendChild(img)
            photoContainer.appendChild(deleteBtn)

            // Вставляем перед кнопкой добавления фото
            const addButton = container.querySelector(".add-photo-button")
            container.insertBefore(photoContainer, addButton)

            // Добавляем обработчик для новой кнопки удаления
            deleteBtn.addEventListener("click", function () {
              handleDeleteAlbumPhoto(this)
            })
          } else {
            console.log(data.error || "Помилка при завантаженні фото")
          }
        })
    })
  })

  function getCookie(name) {
    let cookieValue = null
    if (document.cookie) {
      const cookies = document.cookie.split(";")
      for (const c of cookies) {
        const cookie = c.trim()
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }

  document.querySelectorAll(".cancel").forEach((cancelButton) => {
    cancelButton.addEventListener("click", (event) => {
      event.preventDefault()
      albumForm.style.display = "none"
      editForm.style.display = "none"
    })
  })

  const buttons = document.querySelectorAll(".delete-album-button")

  buttons.forEach((button) => {
    button.addEventListener("mouseenter", () => {
      button.textContent = "🗑"
    })

    button.addEventListener("mouseleave", () => {
      button.textContent = "👁"
    })
  })

  function handleAlbumDeleteClick(button) {
    const albumId = button.dataset.albumId

    if (confirm("Ви впевнені, що хочете видалити цей альбом?")) {
      fetch("/ajax/delete-album/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ album_id: albumId }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            button.closest(".album-content").remove()
          } else {
            console.log(data.error || "Не вдалося видалити альбом")
          }
        })
    }
  }

  document.querySelectorAll(".delete-album-button").forEach((button) => {
    button.addEventListener("click", function () {
      handleAlbumDeleteClick(this)
    })
  })

  document.querySelectorAll(".delete-album-in-menu-button").forEach((button) => {
    button.addEventListener("click", function () {
      handleAlbumDeleteClick(this)
    })
  })

  // відкриття меню до альбому
  const albumMenuBtn = document.querySelectorAll(".open-album-menu")

  albumMenuBtn.forEach((button) => {
    const albumContent = button.closest(".album-content")
    const menu = albumContent.querySelector(".album-menu")

    button.addEventListener("click", () => {
      if (menu.style.display === "flex") {
        menu.style.display = "none"
        button.style.backgroundColor = "#FFFFFF"
      } else {
        menu.style.display = "flex"
        button.style.backgroundColor = "#E9E5EE"
      }
    })
  })

  // для редагування альбома
  document.querySelectorAll(".edit-album-button").forEach((button) => {
    button.addEventListener("click", () => {
      const albumId = button.dataset.albumId
      const albumBlock = button.closest(".album-content")
      const name = albumBlock.querySelector(".album-header-name").innerText
      const topic = albumBlock.querySelector(".theme-and-year h4").innerText
      // const year = albumBlock.querySelector('.theme-and-year h5').innerText;

      document.querySelector("#edit-album-id").value = albumId
      // console.log(document.querySelector('#edit-album-id').value);
      // console.log(albumId);
      document.querySelector("#edit-name-input").value = name
      document.querySelector("#edit-topic-input").value = topic
      // document.querySelector('#id_year').value = year;

      document.querySelector("#edit-album-window-background").style.display = "block"
      document.querySelectorAll(".album-menu").forEach((menu) => {
        menu.style.display = "none"
        document.querySelectorAll(".open-album-menu").forEach((buttonOpenMenu) => {
          buttonOpenMenu.style.backgroundColor = "#FFFFFF"
        })
      })
    })
  })

  // Закриття модалки редагування
  document.querySelector("#exit-edit p").addEventListener("click", () => {
    document.querySelector("#edit-album-window-background").style.display = "none"
  })

  const userAddPhotoBtn = document.getElementById("add-photo")
  const userMainAddBtn = document.getElementById("add-user-photo-main")
  const userPhotoInput = document.getElementById("user-photo-input")
  const userPhotoList = document.getElementById("user-photo-list")
  ;[userAddPhotoBtn, userMainAddBtn].forEach((btn) => {
    if (btn) {
      btn.addEventListener("click", (e) => {
        e.preventDefault()
        userPhotoInput.click()
      })
    }
  })

  if (userPhotoInput) {
    userPhotoInput.addEventListener("change", function () {
      const file = this.files[0]
      if (!file) return

      const formData = new FormData()
      formData.append("file", file)

      fetch("/ajax/upload-user-photo/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            // Создаем контейнер для пользовательского фото с кнопкой удаления
            const photoContainer = document.createElement("div")
            photoContainer.className = "user-photo-container"

            const img = document.createElement("img")
            img.src = data.image_url
            img.alt = "avatar"

            const deleteBtn = document.createElement("button")
            deleteBtn.type = "button"
            deleteBtn.className = "delete-user-photo-btn"
            deleteBtn.dataset.avatarId = data.avatar_id
            deleteBtn.textContent = "🗑"

            photoContainer.appendChild(img)
            photoContainer.appendChild(deleteBtn)

            userPhotoList.insertBefore(photoContainer, userMainAddBtn)

            // Добавляем обработчик для новой кнопки удаления
            deleteBtn.addEventListener("click", function () {
              handleDeleteUserPhoto(this)
            })
          } else {
            console.log(data.error || "Помилка при завантаженні")
          }
        })
    })
  }
  // Функция переключения видимости альбома
  function handleToggleAlbumVisibility(button) {
    const albumId = button.dataset.albumId

    fetch("/ajax/toggle-album-visibility/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ album_id: albumId }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          // Обновляем текст кнопки в зависимости от видимости
          if (data.shown) {
            button.textContent = "👁 Цей альбом бачать всі"
            button.className = "hide-visibility-button menu-button"
          } else {
            button.textContent = "👁 Цей альбом бачите тільки ви"
            button.className = "show-visibility-button menu-button"
          }

          // Закрываем меню
          const menu = button.closest(".album-menu")
          menu.style.display = "none"
          const menuButton = menu.parentElement.querySelector(".open-album-menu")
          menuButton.style.backgroundColor = "#FFFFFF"
        } else {
          console.log(data.error || "Не вдалося змінити видимість альбому")
        }
      })
  }

  // Функция удаления фото из альбома
  function handleDeleteAlbumPhoto(button) {
    const imageId = button.dataset.imageId
    const albumId = button.dataset.albumId

    if (confirm("Ви впевнені, що хочете видалити це фото?")) {
      fetch("/ajax/delete-album-photo/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          image_id: imageId,
          album_id: albumId,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            button.closest(".album-photo-container").remove()
          } else {
            console.log(data.error || "Не вдалося видалити фото")
          }
        })
    }
  }

  // Функция удаления пользовательского фото
  function handleDeleteUserPhoto(button) {
    const avatarId = button.dataset.avatarId

    if (confirm("Ви впевнені, що хочете видалити це фото?")) {
      fetch("/ajax/delete-user-photo/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ avatar_id: avatarId }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            button.closest(".user-photo-container").remove()
          } else {
            console.log(data.error || "Не вдалося видалити фото")
          }
        })
    }
  }

  // Обработчики для кнопок переключения видимости альбома
  document.addEventListener("click", (e) => {
    if (
      e.target.classList.contains("hide-visibility-button") ||
      e.target.classList.contains("show-visibility-button")
    ) {
      handleToggleAlbumVisibility(e.target)
    }
  })

  // Обработчики для кнопок удаления фото из альбомов
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("delete-album-photo-btn")) {
      handleDeleteAlbumPhoto(e.target)
    }
  })

  // Обработчики для кнопок удаления пользовательских фото
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("delete-user-photo-btn")) {
      handleDeleteUserPhoto(e.target)
    }
  })
})
