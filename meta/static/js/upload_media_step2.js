(() => {
    let idTerms = document.querySelector('#id_terms')
    idTerms.addEventListener('click', () => {
        let errorMessage = document.querySelector('.field__errors')
        if (idTerms.checked && errorMessage) {
            errorMessage.remove()
        }
    })


    let dashboardForm = document.querySelector('.dashboard-form')
    dashboardForm.addEventListener('submit', (event) => {
        
        if (!idTerms.checked && event.submitter.value != 'cancel') {
            event.preventDefault()
            
            let termsDiv = document.querySelector('.terms-div')
            if (!termsDiv.contains(document.querySelector('.field__errors'))) {
                let errorMessage = document.createElement('span')
                errorMessage.innerText = 'Você deve aceitar os termos'
                errorMessage.classList.add('field__errors')
                termsDiv.prepend(errorMessage)
            }
        }
    })

    new CreateEntry({ fieldName: 'taxa' })
    new CreateEntry({ fieldName: 'location' })
    new CreateEntry({ fieldName: 'authors' })

    let stateContainer = document.querySelector('.country-container').nextElementSibling
    let cityContainer = document.querySelector('.country-container').nextElementSibling.nextElementSibling
    stateContainer.classList.add('hide-div')
    cityContainer.classList.add('hide-div')
})()