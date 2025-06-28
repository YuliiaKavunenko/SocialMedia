document.addEventListener("DOMContentLoaded", () => {

  // Створення публікації
  const openBtn = document.getElementById("publication-button")
  const modal = document.getElementById("create-publication-form-background")
  const closeBtn = document.getElementById("close-button")

  if (openBtn && modal && closeBtn) {
    openBtn.addEventListener("click", (event) => {
      event.preventDefault()
      modal.style.display = "flex"
      const PublicationsTextArea = document.getElementById("new-publication-input").value
      document.getElementById("form-text").value = PublicationsTextArea
    })

    closeBtn.addEventListener("click", (event) => {
      event.preventDefault()
      modal.style.display = "none"
      document.getElementById("new-tag-form-container").style.display = "none"
      document.getElementById("add-tag-button").style.display = "flex"
      const imagePreview = document.getElementById("image-preview-container")
      if (imagePreview) {
        imagePreview.innerHTML = ""
      }
    })
  }

  // Додавання тега
  const addTagButton = document.getElementById("add-tag-button")
  const tagForm = document.getElementById("new-tag-form-container")

  if (addTagButton && tagForm) {
    addTagButton.addEventListener("click", () => {
      addTagButton.style.display = "none"
      tagForm.style.display = "flex"
    })
  }

  const saveNewTag = document.getElementById("submit-new-tag")
  const newTagInput = document.getElementById("new-tag-input")
  const tagsContainer = document.getElementById("tags-container")

  if (saveNewTag && newTagInput && tagsContainer) {
    saveNewTag.addEventListener("click", () => {
      console.log("Кнопка збереження тега натиснута")

      const newTag = newTagInput.value.trim()

      if (!newTag) {
        console.log("Будь ласка, введіть тег.")
        return
      }

      fetch(ADD_TAG_URL, {
        method: "POST",
        headers: {
          "X-CSRFToken": CSRF_TOKEN,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          tag: newTag,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            const tagElement = document.createElement("span")
            tagElement.classList.add("tag-label")
            tagElement.setAttribute("data-tag-id", data.id)
            tagElement.textContent = `#${data.tag}`
            tagsContainer.insertBefore(tagElement, tagForm)
            newTagInput.value = ""

            // Клік на тег
            tagElement.addEventListener("click", function () {
              const tagId = this.getAttribute("data-tag-id")
              if (this.classList.contains("selected")) {
                this.classList.remove("selected")
                selectedTagIds.delete(tagId)
              } else {
                this.classList.add("selected")
                selectedTagIds.add(tagId)
              }
              hiddenInput.value = Array.from(selectedTagIds).join(",")
            })

            // Скриття форми і додаємо тег
            tagForm.style.display = "none"
            addTagButton.style.display = "flex"
          } else {
            console.log("Помилка: " + data.message)
          }
        })
        .catch((error) => {
          console.error("Помилка під час збереження тега:", error)
          console.log("Щось пішло не так при додаванні тега.")
        })
    })
  }

  // Додавання URL
  const addUrlButton = document.getElementById("add-url-button")
  const submitNewUrlButton = document.getElementById("submit-new-url")
  const newUrlInput = document.getElementById("new-url-input")
  const newUrlFormContainer = document.getElementById("new-url-form-container")
  const urlsList = document.getElementById("urls-list")

  if (addUrlButton && submitNewUrlButton && newUrlInput && newUrlFormContainer && urlsList) {
    addUrlButton.addEventListener("click", () => {
      addUrlButton.style.display = "none"
      newUrlFormContainer.style.display = "flex"
      newUrlInput.focus()
    })

    submitNewUrlButton.addEventListener("click", () => {
      const urlValue = newUrlInput.value.trim()
      if (urlValue !== "") {
        // створюємо новий input з цим URL
        const newInput = document.createElement("input")
        newInput.type = "text"
        newInput.name = "extra_urls"
        newInput.value = urlValue
        newInput.readOnly = true
        newInput.classList.add("url-input-added")
        urlsList.appendChild(newInput)

        // очищаємо поле
        newUrlInput.value = ""
        newUrlFormContainer.style.display = "none"
        addUrlButton.style.display = "flex"
      }
    })
  }

  // Обробка тегів
  const tagLabels = document.querySelectorAll(".tag-label")
  const hiddenInput = document.getElementById("selected-tags-input")

  const selectedTagIds = new Set()

  tagLabels.forEach((tag) => {
    tag.addEventListener("click", function () {
      const tagId = this.getAttribute("data-tag-id")

      if (this.classList.contains("selected")) {
        this.classList.remove("selected")
        selectedTagIds.delete(tagId)
      } else {
        this.classList.add("selected")
        selectedTagIds.add(tagId)
      }

      hiddenInput.value = Array.from(selectedTagIds).join(",")
    })
  })

  // Вибір декількох зображень
  const addImageButton = document.getElementById("add-image-button")
  const imageInput = document.getElementById("id_images")

  if (addImageButton && imageInput) {
    imageInput.setAttribute("multiple", "multiple")

    addImageButton.addEventListener("click", (event) => {
      event.preventDefault()
      imageInput.click()
    })

    imageInput.addEventListener("change", () => {
      if (imageInput.files.length > 9) {
        console.log("Максимально можна додати 9 фотографій")
        return
      }
      if (imageInput.files.length > 0) {
        displayImagePreviews(imageInput.files)
      }
    })
  } else {
    console.warn("Не знайдено кнопку або інпут для вибору файлу")
  }

  // Відображення превью зображень
  function displayImagePreviews(files) {
    let previewContainer = document.getElementById("image-preview-container")

    if (!previewContainer) {
      previewContainer = document.createElement("div")
      previewContainer.id = "image-preview-container"

      const formButtons = document.getElementById("publication-form-buttons")
      formButtons.parentNode.insertBefore(previewContainer, formButtons)
    }

    previewContainer.innerHTML = ""

    const imageCount = files.length
    previewContainer.className = `image-preview-container count-${imageCount}`

    Array.from(files).forEach((file, index) => {
      if (file.type.startsWith("image/")) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const imagePreview = document.createElement("div")
          imagePreview.className = "image-preview-item"

          const img = document.createElement("img")
          img.src = e.target.result
          img.className = "preview-image"

          const removeBtn = document.createElement("button")
          removeBtn.textContent = "🗑"
          removeBtn.className = "remove-image-btn"
          removeBtn.type = "button"
          removeBtn.onclick = () => {
            removeImagePreview(index)
          }

          imagePreview.appendChild(img)
          imagePreview.appendChild(removeBtn)
          previewContainer.appendChild(imagePreview)
        }
        reader.readAsDataURL(file)
      }
    })
  }

  // Видалення превью зображення
  function removeImagePreview(index) {
    const imageInput = document.getElementById("id_images")
    const dt = new DataTransfer()

    Array.from(imageInput.files).forEach((file, i) => {
      if (i !== index) {
        dt.items.add(file)
      }
    })

    imageInput.files = dt.files

    if (imageInput.files.length > 0) {
      displayImagePreviews(imageInput.files)
    } else {
      const previewContainer = document.getElementById("image-preview-container")
      if (previewContainer) {
        previewContainer.innerHTML = ""
      }
    }
  }

  // Адаптивні класи до зображень публікацій
  function applyImageGalleryLayout() {
    document.querySelectorAll(".publication-images-container").forEach((container) => {
      const images = container.querySelectorAll(".publication-image")
      const imageCount = images.length

      container.className = container.className.replace(/\bcount-\d+\b/g, "")
      container.classList.add(`count-${imageCount}`)
    })
  }

  applyImageGalleryLayout()

  // генерація імені користувача
  const trigger = document.getElementById("suggest-username-trigger")
  const firstNameInput = document.querySelector('input[name="first_name"]')
  const lastNameInput = document.querySelector('input[name="last_name"]')
  const usernameInput = document.querySelector('input[name="username"]')

  if (trigger && firstNameInput && lastNameInput && usernameInput) {
    function generateUsername() {
      const first = firstNameInput.value.trim().toLowerCase()
      const last = lastNameInput.value.trim().toLowerCase()
      if (!first || !last) {
        document.getElementById("username-generation-error").style.display = "block"
        document.getElementById("username-generation-error").textContent =
          "Заповніть ім'я та прізвище перед генерацією імені користувача"
        return
      }

      const base = (last + first).replace(/\s+/g, "")
      const randomSuffix = Math.floor(100 + Math.random() * 900)
      const suggested = (base + randomSuffix).slice(0, 15)

      usernameInput.value = suggested
    }

    trigger.addEventListener("click", generateUsername)
  }
})
