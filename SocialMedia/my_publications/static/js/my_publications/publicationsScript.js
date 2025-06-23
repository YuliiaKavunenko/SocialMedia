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

  // Відкриття/закриття меню з трьома крапками
  document.querySelectorAll(".publication-dots").forEach((button) => {
    button.addEventListener("click", function () {
      const menu = this.parentElement.querySelector(".dots-menu")
      const isVisible = menu.style.display === "flex"
      menu.style.display = isVisible ? "none" : "flex"
      this.style.backgroundColor = isVisible ? "#FFFFFF" : "#E9E5EE"
    })
  })

  // Відкриття форми редагування публікації
  document.querySelectorAll(".dots-menu-button.edit").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.preventDefault()
      // Закриваємо меню з трьома крапками
      const allMenus = document.querySelectorAll(".dots-menu")
      allMenus.forEach((menu) => {
        menu.style.display = "none"
      })
      const allDotsButtons = document.querySelectorAll(".publication-dots")
      allDotsButtons.forEach((dot) => {
        dot.style.backgroundColor = "#FFFFFF"
      })

      const pubId = btn.getAttribute("data-id")
      const formBackground = document.getElementById(`edit-publication-form-background-${pubId}`)
      if (formBackground) {
        formBackground.style.display = "flex"
        const publicationCard = btn.closest(".publication-card")

        // Витягуємо дані з data-атрибутів
        const title = publicationCard.getAttribute("data-title")
        const content = publicationCard.getAttribute("data-text")
        const tags = publicationCard.getAttribute("data-tags")
        const url = publicationCard.getAttribute("data-url")
        const extraUrls = publicationCard.getAttribute("data-extra-urls")

        // Заповнюємо поля форми
        const titleInput = document.getElementById(`edit-form-title-${pubId}`)
        const contentInput = document.getElementById(`edit-form-content-${pubId}`)
        const urlInput = document.getElementById(`edit-form-url-${pubId}`)
        const selectedTagsInput = document.getElementById(`edit-selected-tags-input-${pubId}`)

        if (titleInput) titleInput.value = title || ""
        if (contentInput) contentInput.value = content || ""
        if (urlInput) urlInput.value = url || ""

        // Обробка тегів
        if (tags && selectedTagsInput) {
          const tagIds = tags.split(",").filter((id) => id.trim())
          selectedTagsInput.value = tagIds.join(",")

          // Відмічаємо вибрані теги
          const tagLabels = document.querySelectorAll(`#edit-tags-container-${pubId} .edit-tag-label`)
          tagLabels.forEach((label) => {
            const tagId = label.getAttribute("data-tag-id")
            if (tagIds.includes(tagId)) {
              label.classList.add("selected")
            } else {
              label.classList.remove("selected")
            }
          })
        }

        // Обробка додаткових URL
        if (extraUrls) {
          const urlsList = document.getElementById(`edit-urls-list-${pubId}`)
          const urls = extraUrls.split("|||").filter((url) => url.trim())

          urls.forEach((url) => {
            const newInput = document.createElement("input")
            newInput.type = "text"
            newInput.name = "extra_urls"
            newInput.value = url.trim()
            newInput.readOnly = true
            newInput.classList.add("url-input-added")
            urlsList.appendChild(newInput)
          })
        }

        // Ініціалізуємо функціонал для цієї форми редагування
        initializeEditForm(pubId)
      }
    })
  })

  // Функція ініціалізації функціоналу для форми редагування
  function initializeEditForm(pubId) {
    // Теги для редагування
    const editTagLabels = document.querySelectorAll(`#edit-tags-container-${pubId} .edit-tag-label`)
    const editSelectedTagsInput = document.getElementById(`edit-selected-tags-input-${pubId}`)
    const editSelectedTagIds = new Set()

    // Заповнюємо вже вибрані теги
    editTagLabels.forEach((tag) => {
      if (tag.hasAttribute("data-selected") || tag.classList.contains("selected")) {
        const tagId = tag.getAttribute("data-tag-id")
        editSelectedTagIds.add(tagId)
        tag.classList.add("selected")
      }
    })

    if (editSelectedTagsInput) {
      editSelectedTagsInput.value = Array.from(editSelectedTagIds).join(",")
    }

    editTagLabels.forEach((tag) => {
      tag.addEventListener("click", function () {
        const tagId = this.getAttribute("data-tag-id")

        if (this.classList.contains("selected")) {
          this.classList.remove("selected")
          editSelectedTagIds.delete(tagId)
        } else {
          this.classList.add("selected")
          editSelectedTagIds.add(tagId)
        }

        if (editSelectedTagsInput) {
          editSelectedTagsInput.value = Array.from(editSelectedTagIds).join(",")
        }
      })
    })

    // Додавання нових тегів для редагування
    const editAddTagButton = document.getElementById(`edit-add-tag-button-${pubId}`)
    const editTagForm = document.getElementById(`edit-new-tag-form-container-${pubId}`)
    const editSubmitNewTag = document.getElementById(`edit-submit-new-tag-${pubId}`)
    const editNewTagInput = document.getElementById(`edit-new-tag-input-${pubId}`)
    const editTagsContainer = document.getElementById(`edit-tags-container-${pubId}`)

    if (editAddTagButton && editTagForm) {
      editAddTagButton.addEventListener("click", () => {
        editAddTagButton.style.display = "none"
        editTagForm.style.display = "flex"
        editNewTagInput.focus()
      })
    }

    if (editSubmitNewTag && editNewTagInput && editTagsContainer) {
      editSubmitNewTag.addEventListener("click", () => {
        const newTag = editNewTagInput.value.trim()

        if (!newTag) {
          alert("Будь ласка, введіть тег.")
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
              tagElement.classList.add("tag-label", "edit-tag-label")
              tagElement.setAttribute("data-tag-id", data.id)
              tagElement.setAttribute("data-pub-id", pubId)
              tagElement.textContent = data.tag

              // Добавляем обработчик клика для нового тега
              tagElement.addEventListener("click", function () {
                const tagId = this.getAttribute("data-tag-id")

                if (this.classList.contains("selected")) {
                  this.classList.remove("selected")
                  editSelectedTagIds.delete(tagId)
                } else {
                  this.classList.add("selected")
                  editSelectedTagIds.add(tagId)
                }

                if (editSelectedTagsInput) {
                  editSelectedTagsInput.value = Array.from(editSelectedTagIds).join(",")
                }
              })

              editTagsContainer.insertBefore(tagElement, editTagForm)
              editNewTagInput.value = ""

              // Скрываем форму добавления тега и показываем кнопку
              editTagForm.style.display = "none"
              editAddTagButton.style.display = "flex"
            } else {
              alert("Помилка: " + data.message)
            }
          })
          .catch((error) => {
            console.error("Помилка під час збереження тега:", error)
            alert("Щось пішло не так при додаванні тега.")
          })
      })
    }

    // Додавання URL для редагування
    const editAddUrlButton = document.getElementById(`edit-add-url-button-${pubId}`)
    const editSubmitNewUrlButton = document.getElementById(`edit-submit-new-url-${pubId}`)
    const editNewUrlInput = document.getElementById(`edit-new-url-input-${pubId}`)
    const editNewUrlFormContainer = document.getElementById(`edit-new-url-form-container-${pubId}`)
    const editUrlsList = document.getElementById(`edit-urls-list-${pubId}`)

    if (editAddUrlButton && editNewUrlFormContainer && editNewUrlInput) {
      editAddUrlButton.addEventListener("click", () => {
        editAddUrlButton.style.display = "none"
        editNewUrlFormContainer.style.display = "flex"
        editNewUrlInput.focus()
      })
    }

    if (editSubmitNewUrlButton && editNewUrlInput && editUrlsList) {
      editSubmitNewUrlButton.addEventListener("click", () => {
        const urlValue = editNewUrlInput.value.trim()
        if (urlValue !== "") {
          const newInput = document.createElement("input")
          newInput.type = "text"
          newInput.name = "extra_urls"
          newInput.value = urlValue
          newInput.readOnly = true
          newInput.classList.add("url-input-added")
          editUrlsList.appendChild(newInput)

          editNewUrlInput.value = ""
          editNewUrlFormContainer.style.display = "none"
          editAddUrlButton.style.display = "flex"
        }
      })
    }

    // Обробка зображень для редагування
    const editAddImageButton = document.getElementById(`edit-add-image-button-${pubId}`)
    const editImageInput = document.getElementById(`edit-form-images-${pubId}`)

    if (editAddImageButton && editImageInput) {
      editImageInput.setAttribute("multiple", "multiple")

      editAddImageButton.addEventListener("click", (event) => {
        event.preventDefault()
        editImageInput.click()
      })

      editImageInput.addEventListener("change", () => {
        if (editImageInput.files.length > 9) {
          alert("Максимально можна додати 9 фотографій")
          return
        }
        if (editImageInput.files.length > 0) {
          displayEditImagePreviews(editImageInput.files, pubId)
        }
      })
    }

    // Обробка видалення поточних зображень
    const currentImageItems = document.querySelectorAll(`#current-images-container-${pubId} .current-image-item`)
    const imagesToDeleteInput = document.getElementById(`images-to-delete-${pubId}`)
    const imagesToDelete = new Set()

    currentImageItems.forEach((item) => {
      const removeBtn = item.querySelector(".remove-current-image-btn")
      if (removeBtn) {
        removeBtn.addEventListener("click", () => {
          const imageId = removeBtn.getAttribute("data-image-id")

          if (item.classList.contains("removed")) {
            // Відновлюємо зображення
            item.classList.remove("removed")
            imagesToDelete.delete(imageId)
            removeBtn.textContent = "🗑"
            removeBtn.style.backgroundColor = "#ffffff"
          } else {
            // Позначаємо для видалення
            item.classList.add("removed")
            imagesToDelete.add(imageId)
            removeBtn.textContent = "↶"
            removeBtn.style.backgroundColor = "#e9e5ee"
          }

          // Оновлюємо приховане поле
          if (imagesToDeleteInput) {
            imagesToDeleteInput.value = Array.from(imagesToDelete).join(",")
          }
        })
      }
    })
  }

  // Функция для отображения превью изображений в форме редагування
  function displayEditImagePreviews(files, pubId) {
    let previewContainer = document.getElementById(`edit-image-preview-container-${pubId}`)

    if (!previewContainer) {
      previewContainer = document.createElement("div")
      previewContainer.id = `edit-image-preview-container-${pubId}`

      const formButtons = document.getElementById(`edit-publication-form-buttons-${pubId}`)
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
            removeEditImagePreview(index, pubId)
          }

          imagePreview.appendChild(img)
          imagePreview.appendChild(removeBtn)
          previewContainer.appendChild(imagePreview)
        }
        reader.readAsDataURL(file)
      }
    })
  }

  // Функция для удаления превью изображения в форме редагування
  function removeEditImagePreview(index, pubId) {
    const imageInput = document.getElementById(`edit-form-images-${pubId}`)
    const dt = new DataTransfer()

    Array.from(imageInput.files).forEach((file, i) => {
      if (i !== index) {
        dt.items.add(file)
      }
    })

    imageInput.files = dt.files

    if (imageInput.files.length > 0) {
      displayEditImagePreviews(imageInput.files, pubId)
    } else {
      const previewContainer = document.getElementById(`edit-image-preview-container-${pubId}`)
      if (previewContainer) {
        previewContainer.innerHTML = ""
      }
    }
  }

  // Закриття форми редагування при кліку поза нею
  document.querySelectorAll(".edit-publication-form-background").forEach((formBg) => {
    formBg.addEventListener("click", (event) => {
      if (event.target === formBg) {
        formBg.style.display = "none"
      }
    })
  })

  // Кнопка закриття форми редагування
  document.querySelectorAll(".edit-close-button").forEach((closeBtn) => {
    closeBtn.addEventListener("click", (event) => {
      event.preventDefault()
      const parentForm = closeBtn.closest(".edit-publication-form-background")
      if (parentForm) {
        parentForm.style.display = "none"
      }
    })
  })

  // Обробка кнопки видалення публікації
  document.querySelectorAll(".dots-menu-button.delete").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.preventDefault()
      const pubId = btn.getAttribute("data-id")
      if (confirm("Ви впевнені, що хочете видалити цю публікацію?")) {
        const form = document.getElementById(`delete-publication-form-${pubId}`)
        if (form) {
          form.submit()
        }
      }
    })
  })

  // Додавання тега (для форми створення)
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
      const newTag = newTagInput.value.trim()

      if (!newTag) {
        alert("Будь ласка, введіть тег.")
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

            tagElement.addEventListener("click", function () {
              const tagId = this.getAttribute("data-tag-id")
              const hiddenInput = document.getElementById("selected-tags-input")

              if (this.classList.contains("selected")) {
                this.classList.remove("selected")
                selectedTagIds.delete(tagId)
              } else {
                this.classList.add("selected")
                selectedTagIds.add(tagId)
              }

              hiddenInput.value = Array.from(selectedTagIds).join(",")
            })

            tagsContainer.insertBefore(tagElement, tagForm)
            newTagInput.value = ""

            tagForm.style.display = "none"
            addTagButton.style.display = "flex"
          } else {
            alert("Помилка: " + data.message)
          }
        })
        .catch((error) => {
          console.error("Помилка під час збереження тега:", error)
          alert("Щось пішло не так при додаванні тега.")
        })
    })
  }

  // Додавання URL (для форми створення)
  const addUrlButton = document.getElementById("add-url-button")
  const submitNewUrlButton = document.getElementById("submit-new-url")
  const newUrlInput = document.getElementById("new-url-input")
  const newUrlFormContainer = document.getElementById("new-url-form-container")
  const urlsList = document.getElementById("urls-list")

  if (addUrlButton && newUrlFormContainer && newUrlInput) {
    addUrlButton.addEventListener("click", () => {
      addUrlButton.style.display = "none"
      newUrlFormContainer.style.display = "flex"
      newUrlInput.focus()
    })
  }

  if (submitNewUrlButton && newUrlInput && urlsList) {
    submitNewUrlButton.addEventListener("click", () => {
      const urlValue = newUrlInput.value.trim()
      if (urlValue !== "") {
        const newInput = document.createElement("input")
        newInput.type = "text"
        newInput.name = "extra_urls"
        newInput.value = urlValue
        newInput.readOnly = true
        newInput.classList.add("url-input-added")
        urlsList.appendChild(newInput)

        newUrlInput.value = ""
        newUrlFormContainer.style.display = "none"
        addUrlButton.style.display = "flex"
      }
    })
  }

  // Обробка тегів (для форми створення)
  const tagLabels = document.querySelectorAll(".tag-label:not(.edit-tag-label)")
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

      if (hiddenInput) {
        hiddenInput.value = Array.from(selectedTagIds).join(",")
      }
    })
  })

  // Обработка множественного выбора изображений (для форми створення)
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
        alert("Максимально можна додати 9 фотографій")
        return
      }
      if (imageInput.files.length > 0) {
        displayImagePreviews(imageInput.files)
      }
    })
  }

  // Функция для отображения превью изображений (для форми створення)
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

  // Функция для удаления превью изображения (для форми створення)
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

  // Функция для применения адаптивных классов к галереям изображений в публікациях
  function applyImageGalleryLayout() {
    document.querySelectorAll(".publication-images-container").forEach((container) => {
      const images = container.querySelectorAll(".publication-image")
      const imageCount = images.length

      container.className = container.className.replace(/\bcount-\d+\b/g, "")
      container.classList.add(`count-${imageCount}`)
    })
  }

  applyImageGalleryLayout()
})
