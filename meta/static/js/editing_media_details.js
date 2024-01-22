(() => {
    const modals = document.querySelectorAll('[data-modal]:not([data-modal="references"]):not([data-modal="latitude"])')
    modals.forEach(modal => {
        const modalName = modal.dataset.modal
        
        new Modal({
            modalContent: document.querySelector(`[data-modal='${modalName}']`),
            modalTrigger: document.querySelector(`[data-open-modal='${modalName}']`),
            modalClose: document.querySelector(`[data-close-modal='${modalName}']`)
        })
    })
})()