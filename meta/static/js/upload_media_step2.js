(() => {
    let idTerms = document.querySelector('#id_terms')
    idTerms.addEventListener('click', () => {
        let errorMessage = document.querySelector('.field-error')
        if (idTerms.checked && errorMessage) {
            errorMessage.remove()
        }
    })


    let dashboardForm = document.querySelector('.dashboard-form')
    dashboardForm.addEventListener('submit', (event) => {
        
        if (!idTerms.checked && event.submitter.value != 'cancel') {
            event.preventDefault()
            
            let termsDiv = document.querySelector('.terms-div')
            if (!termsDiv.contains(document.querySelector('.field-error'))) {
                let errorMessage = document.createElement('span')
                errorMessage.innerText = 'Você deve aceitar os termos'
                errorMessage.classList.add('field-error')
                termsDiv.prepend(errorMessage)
            }
        }
    })


    const modals = document.querySelectorAll('[data-modal]:not([data-modal="references"]):not([data-modal="latitude"])')
    modals.forEach(modal => {
        const modalName = modal.dataset.modal
        new Modal({
            modalContent: document.querySelector(`[data-modal='${modalName}']`),
            modalTrigger: document.querySelector(`[data-open-modal='${modalName}']`),
            modalClose: document.querySelector(`[data-close-modal='${modalName}']`)
        })
    })


    let stateContainer = document.querySelector('.country-container').nextElementSibling
    let cityContainer = document.querySelector('.country-container').nextElementSibling.nextElementSibling
    stateContainer.classList.add('hide-div')
    cityContainer.classList.add('hide-div')
})()