class Modal {
    modalTrigger
    modalClose
    modalOverlay
    modalContent
    focusableElements
    isModalOpened = false

    constructor({ modalContent, modalTrigger, modalClose}) {
        this.modalTrigger = modalTrigger
        this.modalClose = modalClose
        this.modalContent = modalContent

        // TODO: improve this
        this.modalOverlay = document.createElement('div')
        this.modalOverlay.classList.add('modal-overlay')
        document.body.append(this.modalOverlay)

        this.focusableElements = Array.from(
            this.modalContent.querySelectorAll(
                'button, input:not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])'
            )
        )

        this.modalTrigger?.addEventListener('click', this.showModal.bind(this))
        this.modalClose?.addEventListener('click', this.closeModal.bind(this))
        this.modalOverlay.addEventListener('click', () => {
            this.closeModal()
        })
    }

    showModal() {
        this.modalOverlay.classList.add('opened-behind-modal')
        this.modalContent.classList.add('opened-modal')
        this.modalContent.style.transition = '.3s'
        document.documentElement.style.overflow = 'hidden'
        this.isModalOpened = true

        this.modalContent.addEventListener('keydown', this.handleTabKey.bind(this))

        this.modalClose.focus()
    }

    closeModal() {
        this.modalOverlay.classList.remove('opened-behind-modal')
        this.modalContent.classList.remove('opened-modal')
        this.modalContent.style.transition = '0s'
        document.documentElement.style.removeProperty('overflow')
        this.isModalOpened = false

        this.modalContent.removeEventListener('keydown', this.handleTabKey.bind(this))
        this.modalTrigger.focus()
    }

    handleTabKey(event) {
        const firstElement = this.focusableElements[0]
        const lastElement = this.focusableElements[this.focusableElements.length - 1]

        if (event.key.toLowerCase() === 'tab') {
            if (event.shiftKey && document.activeElement === firstElement) {
                event.preventDefault()
                lastElement.focus()
            } else if (!event.shiftKey && document.activeElement === lastElement) {
                event.preventDefault()
                firstElement.focus()
            }
        }
    }
}