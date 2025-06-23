document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("delete-user-modal")
    const modalOverlay = document.querySelector(".modal-overlay")
    const closeBtn = document.querySelector(".modal-close")
    const cancelBtn = document.querySelector(".cancel-delete-user")
    const confirmBtn = document.querySelector(".confirm-delete-user")

    const deleteButtons = document.querySelectorAll(".delete-request, .delete-recommendation, .delete-friend")

    let currentUserToDelete = null

    function showModal(userData = null) {
        currentUserToDelete = userData
        modalOverlay.classList.add("active")
        document.body.style.overflow = "hidden"
    }

    function hideModal() {
        modalOverlay.classList.remove("active")
        document.body.style.overflow = "auto"
        currentUserToDelete = null
    }

    deleteButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
        e.preventDefault()

        const card = this.closest(".card")
        const userName = card.querySelector("h3").textContent
        const userHandle = card.querySelector("h4").textContent

        currentUserToDelete = {
            name: userName,
            handle: userHandle,
            element: card,
            button: this,
        }

        showModal(currentUserToDelete)
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

    confirmBtn.addEventListener("click", (e) => {
        e.preventDefault()

        if (currentUserToDelete) {
        console.log("Deleting user:", currentUserToDelete.name)
        currentUserToDelete.element.remove()


        }

        hideModal()
    })
})
