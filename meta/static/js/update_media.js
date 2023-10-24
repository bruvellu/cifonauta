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

    if (!modalContainer?.contains(event.target) && 
        !otherButton?.contains(event.target) &&
        isModalOpened) {
            closeModal()
    }
})


let stateContainer = document.querySelector('.country-container').nextElementSibling
let cityContainer = document.querySelector('.country-container').nextElementSibling.nextElementSibling
let countryField = document.querySelector('#id_country')
if (countryField.options[countryField.selectedIndex].value != 1) {
    stateContainer.classList.add('hide-div')
    cityContainer.classList.add('hide-div')
} else {
    let stateField = document.querySelector('#id_state')
    let cityField = document.querySelector('#id_city')
    
    stateField.required = true
    cityField.required = true
}

//Synchronize Country, State and City fields
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
        function createNullOption() {
            let option = document.createElement('option')
            option.value = ''
            option.selected = ''
            option.innerText = '---------'
            return option
        }
        
        let stateField = document.querySelector('#id_state')
        stateField.innerHTML = ''
        stateField.append(createNullOption())

        const states = data.states
        states?.forEach(state => {
            option = document.createElement('option')
            option.value = state.id
            option.innerText = state.name
            stateField.append(option)
        })

        let cityField = document.querySelector('#id_city')
        cityField.innerHTML = ''
        cityField.append(createNullOption())

        if (e.target.options[e.target.selectedIndex].value == 1) {
            stateContainer.classList.remove('hide-div')
            cityContainer.classList.remove('hide-div')

            stateField.required = true
            cityField.required = true
        } else {
            stateContainer.classList.add('hide-div')
            cityContainer.classList.add('hide-div')

            stateField.required = false
            cityField.required = false
        }
    })
})

let stateField = document.querySelector('#id_state')
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