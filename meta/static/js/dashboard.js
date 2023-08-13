let hasTaxon = document.querySelector('#id_has_taxons_0')
let noTaxon = document.querySelector('#id_has_taxons_1')
let taxonsDiv = document.querySelector('.taxons-div')

noTaxon.parentNode.parentNode.classList.add('taxons-button-checked')

hasTaxon.addEventListener('click', () => {
    taxonsDiv.classList.remove('hide-div')
    
    noTaxon.parentNode.parentNode.classList.remove('taxons-button-checked')
    hasTaxon.parentNode.parentNode.classList.add('taxons-button-checked')
})

noTaxon.addEventListener('click', () => {
    taxonsDiv.classList.add('hide-div')

    hasTaxon.parentNode.parentNode.classList.remove('taxons-button-checked')
    noTaxon.parentNode.parentNode.classList.add('taxons-button-checked')
})


let preRegistrationButton = document.querySelector('.pre-registration-button')
let closeRegistrationButton = document.querySelector('.close-registration-button')
let modal = document.querySelector('dialog')

preRegistrationButton.onclick = () => {
    modal.showModal()
}

closeRegistrationButton.onclick = () => {
    modal.close()
}

// document.addEventListener('click', (event)=>{
//     if (!modal.contains(event.target) && 
//         !preRegistrationButton.contains(event.target) &&
//         modal.open) {
//             modal.close()
//     }
// })