let locationModal = document.querySelector('#location-modal')
let openLocationModalBtn = document.querySelector('#open-location-modal-btn')
let closeLocationModalBtn = document.querySelector('#close-location-modal-btn')

const locationModalHandler = new ModalHandler({
    modalContent: locationModal,
    modalTrigger: openLocationModalBtn,
    modalClose: closeLocationModalBtn
})