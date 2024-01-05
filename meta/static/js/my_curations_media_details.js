let modalContainer = document.querySelector('#modal-container')
let openModalButton = document.querySelector('#open-modal-button')
let closeModalButton = document.querySelector('#close-modal-button')

const modalHandler = new Modal({ 
    modalContent: modalContainer,
    modalTrigger: openModalButton,
    modalClose: closeModalButton
})