let curationsListAll = document.querySelectorAll('.curations-list')
let curationsListArray = Array.from(curationsListAll)

curationsListArray.forEach(curationList => {
  if (curationList.children.length > 3) {
    let input = document.createElement('input')
    input.setAttribute('type', 'checkbox')
    input.classList.add('expand-curations')
  
    curationList.insertAdjacentElement('afterend', input)
  }
})

let entriesNumberButton = document.querySelector('#entries-number-button')
entriesNumberButton.addEventListener('click', () => {
  entriesNumberButton.querySelector('img').classList.add('rotate-animation')
})


let modalContainer = document.querySelector('#modal-container')
let openModalButton = document.querySelector('#open-modal-button')
let closeModalButton = document.querySelector('#close-modal-button')
const modalHandler = new Modal({ 
    modalContent: modalContainer,
    modalTrigger: openModalButton,
    modalClose: closeModalButton
})