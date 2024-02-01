class Modal {
    modalTrigger
    modalClose
    modalOverlay
    modalContent
    modalZIndex
    onCloseCallback

    constructor({ modalContent, modalTrigger, modalClose, onCloseCallback = null, modalZIndex = 5}) {
        this.modalTrigger = modalTrigger
        this.modalClose = modalClose
        this.modalContent = modalContent
        this.onCloseCallback = onCloseCallback
        this.modalZIndex = modalZIndex

        this.modalContent.classList.add('modal-container')
        this.modalContent.style.zIndex = this.modalZIndex

        this.modalOverlay = document.createElement('div')
        this.modalOverlay.classList.add('overlay', 'overlay--dark')
        this.modalOverlay.style.zIndex = this.modalZIndex - 1
        
        this.modalContent?.addEventListener('keydown', this.handleTabKey.bind(this))
        this.modalTrigger?.addEventListener('click', this.showModal.bind(this))
        this.modalClose?.addEventListener('click', this.closeModal.bind(this))
        this.modalOverlay.addEventListener('click', this.closeModal.bind(this))
    }

    showModal() {
        this.modalContent.classList.add('opened-modal-container')
        this.modalContent.style.transition = '.3s'
        document.documentElement.style.overflow = 'hidden'

        document.body.append(this.modalOverlay)

        this.modalClose?.focus()
    }

    closeModal() {
        this.modalContent.classList.remove('opened-modal-container')
        this.modalContent.style.transition = '0s'
        document.documentElement.style.removeProperty('overflow')

        this.modalOverlay.remove()

        this.modalTrigger?.focus()

        if (typeof this.onCloseCallback === 'function') {
            this.onCloseCallback();
        }
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