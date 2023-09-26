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