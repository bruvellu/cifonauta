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

        this.modalOverlay = document.createElement('div')
        this.modalOverlay.classList.add('modal-overlay')
        document.body.append(this.modalOverlay)

        this.modalTrigger?.addEventListener('click', this.showModal.bind(this));
        this.modalClose?.addEventListener('click', this.closeModal.bind(this));
        this.modalOverlay.addEventListener('click', (event) => {
            if (!this.modalContent?.contains(event.target) && 
                !this.modalTrigger?.contains(event.target) &&
                this.isModalOpened) {
                    this.closeModal()
            }
        })
    }

    showModal() {
        this.modalOverlay.classList.add('opened-behind-modal');
        this.modalContent.classList.add('opened-modal');
        this.modalContent.style.transition = '.3s';
        document.documentElement.style.overflow = 'hidden';
        this.isModalOpened = true;
    }

    closeModal() {
        this.modalOverlay.classList.remove('opened-behind-modal');
        this.modalContent.classList.remove('opened-modal');
        this.modalContent.style.transition = '0s';
        document.documentElement.style.removeProperty('overflow');
        this.isModalOpened = false;
    }
}