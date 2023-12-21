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


let modalContainer = document.querySelector('#modal-container')
let openModalButton = document.querySelector('#open-modal-button')
let closeModalButton = document.querySelector('#close-modal-button')

const modalHandler = new ModalHandler({ 
    modalContent: modalContainer,
    modalTrigger: openModalButton,
    modalClose: closeModalButton
})

let locationModal = document.querySelector('#location-modal')
let openLocationModalBtn = document.querySelector('#open-location-modal-btn')
let closeLocationModalBtn = document.querySelector('#close-location-modal-btn')

const locationModalHandler = new ModalHandler({
    modalContent: locationModal,
    modalTrigger: openLocationModalBtn,
    modalClose: closeLocationModalBtn
})


let stateContainer = document.querySelector('.country-container').nextElementSibling
let cityContainer = document.querySelector('.country-container').nextElementSibling.nextElementSibling
stateContainer.classList.add('hide-div')
cityContainer.classList.add('hide-div')