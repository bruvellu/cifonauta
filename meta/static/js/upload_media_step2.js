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


let preRegistrationButton = document.querySelector('.pre-registration-button')
let closeModalButton = document.querySelector('.close-modal-button')
let modal = document.querySelector('dialog')

preRegistrationButton.addEventListener('click', () => {
    modal.showModal()
})
closeModalButton.addEventListener('click', () => {
    modal.close()
})


let idTerms = document.querySelector('#id_terms')
idTerms.addEventListener('click', () => {
    let errorMessage = document.querySelector('.field-error')
    if (idTerms.checked && errorMessage) {
        errorMessage.remove()
    }
})

let uploadForm = document.querySelector('.upload-form')
uploadForm.addEventListener('submit', (event) => {
    
    if (!idTerms.checked && event.submitter.value != 'cancel') {
        event.preventDefault()
        
        let termsDiv = document.querySelector('.terms-div')
        if (!termsDiv.contains(document.querySelector('.field-error'))) {
            let errorMessage = document.createElement('span')
            errorMessage.innerText = 'Você deve aceitar os termos'
            errorMessage.classList.add('field-error')
            termsDiv.prepend(errorMessage)
        }
    }
})

let messagesDiv = document.querySelector('.messages-div')
if (messagesDiv) {
    setInterval(() => {
        messagesDiv.remove()
    }, 10000)
}


//Synchronize Country, State and City fields
let stateField = document.querySelector('#id_state')

stateField.innerHTML = ''
let option = document.createElement('option')
option.value = ''
option.selected = ''
option.innerText = '---------'
stateField.append(option)

let cityField = document.querySelector('#id_city')

cityField.innerHTML = ''
option = document.createElement('option')
option.value = ''
option.selected = ''
option.innerText = '---------'
cityField.append(option)


let countryField = document.querySelector('#id_country')
countryField.addEventListener('change', (e) => {
    const url = window.location.origin
    const countryId = e.target.options[e.target.selectedIndex].value

    fetch(`${url}/synchronize-fields?country_id=${countryId}`, {
        method: "GET"
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        }
    })
    .then(data => {
        let stateField = document.querySelector('#id_state')
        
        stateField.innerHTML = ''
        let option = document.createElement('option')
        option.value = ''
        option.selected = ''
        option.innerText = '---------'
        stateField.append(option)

        const states = data.states
        states?.forEach(state => {
            option = document.createElement('option')
            option.value = state.id
            option.innerText = state.name
            stateField.append(option)
        })
    })
})

stateField = document.querySelector('#id_state')
stateField.addEventListener('change', (e) => {
    const url = window.location.origin
    const stateId = e.target.options[e.target.selectedIndex].value

    fetch(`${url}/synchronize-fields?state_id=${stateId}`, {
        method: "GET"
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        }
    })
    .then(data => {
        let cityField = document.querySelector('#id_city')
        
        cityField.innerHTML = ''
        let option = document.createElement('option')
        option.value = ''
        option.selected = ''
        option.innerText = '---------'
        cityField.append(option)
        
        const cities = data.cities
        cities?.forEach(city => {
            option = document.createElement('option')
            option.value = city.id
            option.innerText = city.name
            cityField.append(option)
        })
    })
})