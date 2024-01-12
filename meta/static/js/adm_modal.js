class Modal {
    modalTrigger
    modalClose
    modalOverlay
    modalContent
    isModalOpened = false

    constructor({ modalContent, modalTrigger, modalClose}) {
        this.modalTrigger = modalTrigger
        this.modalClose = modalClose
        this.modalContent = modalContent

        // TODO: improve this
        this.modalOverlay = document.createElement('div')
        this.modalOverlay.classList.add('modal-overlay')
        document.body.append(this.modalOverlay)

        this.modalContent?.addEventListener('keydown', this.handleTabKey.bind(this))
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

        this.modalClose.focus()
    }

    closeModal() {
        this.modalOverlay.classList.remove('opened-behind-modal')
        this.modalContent.classList.remove('opened-modal')
        this.modalContent.style.transition = '0s'
        document.documentElement.style.removeProperty('overflow')
        this.isModalOpened = false

        this.modalTrigger.focus()
    }

    handleTabKey(event) {
        const focusableElements = this.getFocusables()

        const firstFocusable = focusableElements[0]
        const lastFocusable = focusableElements[focusableElements.length - 1]

        if (event.key === 'Tab') {
            if (event.shiftKey && document.activeElement === firstFocusable) {
                event.preventDefault()
                lastFocusable.focus()
            } else if (!event.shiftKey && document.activeElement === lastFocusable) {
                event.preventDefault()
                firstFocusable.focus()
            }
        }
    }

    getFocusables() {
        return (
          [...this.modalContent.querySelectorAll(
              'a, button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])')
          ].filter(elem => {
              if(!elem.hasAttribute('disabled') && !elem.hasAttribute('hidden') && elem.type != 'hidden') return elem
          })
        )
    }
}