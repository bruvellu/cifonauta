// NEEDS 4 TAGS IN THE HTML WITH THE IDs: "behind-modal-container", "modal-container", "open-modal-button", "close-modal-button"
function showModal() {
    const behindModalContainer = document.querySelector('#behind-modal-container')
    behindModalContainer?.classList.add('opened-behind-modal')

    modalContainer.classList.add('opened-modal')
    modalContainer.style.transition = '.3s'

    document.documentElement.style.overflow = 'hidden'
    isModalOpened = true
}

function closeModal() {
    const behindModalContainer = document.querySelector('#behind-modal-container')
    behindModalContainer?.classList.remove('opened-behind-modal')

    modalContainer.classList.remove('opened-modal')
    modalContainer.style.transition = '0s'

    document.documentElement.style.removeProperty('overflow') 
    isModalOpened = false
}

var isModalOpened = false
let modalContainer = document.querySelector('#modal-container')
let openModalButton = document.querySelector('#open-modal-button')
let closeModalButton = document.querySelector('#close-modal-button')


openModalButton.addEventListener('click', showModal)

closeModalButton.addEventListener('click', closeModal)

// Popup closes without clicking on #close-modal-button
// document.addEventListener('click', (event)=>{
//     if (!modalContainer?.contains(event.target) && 
//         !openModalButton?.contains(event.target) &&
//         isModalOpened) {
//             closeModal()
//     }
// })