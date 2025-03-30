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

    sync_location_fields(false)

    const moreFieldsButton = document.querySelector('[data-more-fields-button]')
    moreFieldsButton.addEventListener('click', () => {
        const moreFieldsDiv = moreFieldsButton.nextElementSibling
        
        const moreFieldsState = moreFieldsButton.dataset.state

        if (moreFieldsState == 'close') {
            moreFieldsDiv.style.display = 'flex'
            
            moreFieldsButton.setAttribute('data-state', 'open')
        }
        else {
            moreFieldsDiv.style.display = ''

            moreFieldsButton.setAttribute('data-state', 'close')
        }
    })
})()