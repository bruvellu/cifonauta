let mediasInput = document.querySelector('#medias')
mediasInput.addEventListener('change', (e) => {
    let mediasList = Array.from(e.target.files)
    let filesNames = document.querySelector('.files-names')
    if (mediasList.length > 1) {
        console.log(filesNames)
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

preRegistrationButton.addEventListener('click', () => {
    modal.showModal()
})
closeRegistrationButton.addEventListener('click', () => {
    modal.close()
})