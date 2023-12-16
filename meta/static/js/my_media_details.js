let modalContainer = document.querySelector('#modal-container')
let openModalButton = document.querySelector('#open-modal-button')
let closeModalButton = document.querySelector('#close-modal-button')

const modalHandler = new ModalHandler({ 
    modalContent: modalContainer,
    modalTrigger: openModalButton,
    modalClose: closeModalButton
})

let coauthorModalContainer = document.querySelector('#coauthor-modal-container')
let coauthorModalCloseBtn = document.querySelector('#coauthor-modal-close-btn')
let coauthorModalOpenBtn = document.querySelector('#coauthor-modal-open-btn')

const coauthorModal = new ModalHandler({ 
    modalContent: coauthorModalContainer,
    modalTrigger: coauthorModalOpenBtn,
    modalClose: coauthorModalCloseBtn
})