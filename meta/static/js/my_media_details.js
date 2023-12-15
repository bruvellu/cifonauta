let stateContainer = document.querySelector('.country-container').nextElementSibling
let cityContainer = document.querySelector('.country-container').nextElementSibling.nextElementSibling
let countryField = document.querySelector('#id_country')
if (countryField.options[countryField.selectedIndex].value != 1) {
    stateContainer.classList.add('hide-div')
    cityContainer.classList.add('hide-div')
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
        } else {
            stateContainer.classList.add('hide-div')
            cityContainer.classList.add('hide-div')
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