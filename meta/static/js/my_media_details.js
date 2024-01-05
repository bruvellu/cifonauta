let modalContainer = document.querySelector('#modal-container')
let openModalButton = document.querySelector('#open-modal-button')
let closeModalButton = document.querySelector('#close-modal-button')
const modalHandler = new Modal({ 
    modalContent: modalContainer,
    modalTrigger: openModalButton,
    modalClose: closeModalButton
})


let coauthorModalContainer = document.querySelector('#coauthor-modal-container')
let coauthorModalCloseBtn = document.querySelector('#coauthor-modal-close-btn')
let coauthorModalOpenBtn = document.querySelector('#coauthor-modal-open-btn')
const coauthorModal = new Modal({ 
    modalContent: coauthorModalContainer,
    modalTrigger: coauthorModalOpenBtn,
    modalClose: coauthorModalCloseBtn
})


let locationModal = document.querySelector('#location-modal')
let openLocationModalBtn = document.querySelector('#open-location-modal-btn')
let closeLocationModalBtn = document.querySelector('#close-location-modal-btn')
const locationModalHandler = new Modal({
    modalContent: locationModal,
    modalTrigger: openLocationModalBtn,
    modalClose: closeLocationModalBtn
})


let taxaModal = document.querySelector('#taxa-modal')
let openTaxaModalBtn = document.querySelector('#open-taxa-modal-btn')
let closeTaxaModalBtn = document.querySelector('#close-taxa-modal-btn')
const taxaModalHandler = new Modal({
    modalContent: taxaModal,
    modalTrigger: openTaxaModalBtn,
    modalClose: closeTaxaModalBtn
})