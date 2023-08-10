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