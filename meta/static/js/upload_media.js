let mediasInput = document.querySelector('#medias')
mediasInput.addEventListener('change', (e) => {
    let mediasList = Array.from(e.target.files)
    let filesNames = document.querySelector('.files-names')
    if (mediasList.length > 1) {
        if (filesNames) {
            filesNames.innerHTML = ''

            mediasList.map(media => {
                let li = document.createElement('li')
                li.innerText = media.name
                filesNames.appendChild(li)
            })
        } else {
            let ul = document.createElement('ul')
            ul.classList.add('files-names')

            mediasList.map(media => {
                let li = document.createElement('li')
                li.innerText = media.name
                ul.appendChild(li)
            })

            let fileDiv = document.querySelector('.file-div')
            fileDiv.append(ul)
        }
        
    } else {
        filesNames.remove()
    }
})

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
let closeRegistrationButton = document.querySelector('.close-registration-button')
let modal = document.querySelector('dialog')

preRegistrationButton.addEventListener('click', () => {
    modal.showModal()
})
closeRegistrationButton.addEventListener('click', () => {
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

    if (!idTerms.checked) {
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