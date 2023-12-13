let filesInput = document.querySelector('#files')
let stepsBar = document.querySelector('.steps-bar')

filesInput.addEventListener('change', (e) => {
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
        if (filesNames) {
            filesNames.remove()
        }
    }

    mediasList.length >= 1 ? stepsBar.classList.add('mid-step-bar') : stepsBar.classList.remove('mid-step-bar')
})