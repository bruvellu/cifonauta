let hasTaxon = document.querySelector('#id_has_taxons_0')
let noTaxon = document.querySelector('#id_has_taxons_1')
let taxonsDiv = document.querySelector('.taxons-div')

hasTaxon.addEventListener('click', () => {
    taxonsDiv.classList.remove('hide-div')
    hasTaxon.checked = true
})

noTaxon.addEventListener('click', () => {
    taxonsDiv.classList.add('hide-div')
    noTaxon.checked = true
})

let message = document.querySelector('.success')
if (message) {
    setInterval(() => {
        message.remove()
    }, 10000)
}

var isModalOpened = false
function showModal() {
    const behindModalContainer = document.querySelector('.behind-modal-container')
    behindModalContainer.classList.add('opened-behind-modal')

    const modalContainer = document.querySelector('.modal-container')
    modalContainer.classList.add('opened-modal')
    modalContainer.style.transition = '.3s'

    document.documentElement.style.overflow = 'hidden'
    isModalOpened = true
}

function closeModal() {
    const behindModalContainer = document.querySelector('.behind-modal-container')
    behindModalContainer.classList.remove('opened-behind-modal')

    const modalContainer = document.querySelector('.modal-container')
    modalContainer.classList.remove('opened-modal')
    modalContainer.style.transition = '0s'

    document.documentElement.style.removeProperty('overflow') 
    isModalOpened = false
}

document.addEventListener('click', (event)=>{
    const modalContainer = document.querySelector('.modal-container')
    const otherButton = document.querySelector('.other-button')

    if (!modalContainer.contains(event.target) && 
        !otherButton.contains(event.target) &&
        isModalOpened) {
            closeModal()
    }
})