function sync_location_fields(bashActionsForm = true) {
    let countryContainer = document.querySelector('[data-country-field-container]')
    let stateContainer = countryContainer.nextElementSibling
    let cityContainer = countryContainer.nextElementSibling.nextElementSibling
    let countryField = countryContainer.querySelector('#id_country')
    let stateField = stateContainer.querySelector('#id_state')
    let cityField = cityContainer.querySelector('#id_city')
    let nullOption = cityField.children[0].cloneNode(true)
    
    if (bashActionsForm) {
        stateField.innerHTML = ''
        stateField.append(nullOption.cloneNode(true))
        cityField.innerHTML = ''
        cityField.append(nullOption.cloneNode(true))
    } else {
        // Checking if it is Brasil by its id
        if (countryField.options[countryField.selectedIndex].value != 1) {
            stateContainer.classList.add('hide-div')
            cityContainer.classList.add('hide-div')
        }
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
            stateField.innerHTML = ''
            stateField.append(nullOption.cloneNode(true))
    
            const states = data.states
            states?.forEach(state => {
                option = document.createElement('option')
                option.value = state.id
                option.innerText = state.name
                stateField.append(option)
            })
    
            cityField.innerHTML = ''
            cityField.append(nullOption.cloneNode(true))
            
            if (!bashActionsForm) {
                if (e.target.options[e.target.selectedIndex].value == 1) {
                    stateContainer.classList.remove('hide-div')
                    cityContainer.classList.remove('hide-div')
                } else {
                    stateContainer.classList.add('hide-div')
                    cityContainer.classList.add('hide-div')
                }
            }
        })
    })
    
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
            cityField.innerHTML = ''
            cityField.append(nullOption.cloneNode(true))
            
            const cities = data.cities
            cities?.forEach(city => {
                option = document.createElement('option')
                option.value = city.id
                option.innerText = city.name
                cityField.append(option)
            })
        })
    })
}