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