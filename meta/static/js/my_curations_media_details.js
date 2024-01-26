(() => {
    new Modal({
        modalContent: document.querySelector('[data-modal="media-changes"]'),
        modalTrigger: document.querySelector('[data-open-modal="media-changes"]'),
        modalClose: document.querySelector('[data-close-modal="media-changes"]')
    })
    
    new CreateEntry({ fieldName: 'taxa' })
    new CreateEntry({ fieldName: 'location' })
})()