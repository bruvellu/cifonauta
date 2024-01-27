(() => {
    const mediaChangesModal = document.querySelector('[data-modal="media-changes"]')
    if (mediaChangesModal) {
        new Modal({
            modalContent: mediaChangesModal,
            modalTrigger: document.querySelector('[data-open-modal="media-changes"]'),
            modalClose: document.querySelector('[data-close-modal="media-changes"]')
        })
    }
    
    new CreateEntry({ fieldName: 'taxa' })
    new CreateEntry({ fieldName: 'location' })
})()