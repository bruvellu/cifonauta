(() => {
    let curationsListAll = document.querySelectorAll('.curations-list')
    let curationsListArray = Array.from(curationsListAll)
    curationsListArray.forEach(curationList => {
        if (curationList.children.length > 3) {
            let input = document.createElement('input')
            input.setAttribute('type', 'checkbox')
            input.classList.add('expand-curations')
          
            curationList.insertAdjacentElement('afterend', input)
        }
    })


    let entriesNumberSubmit = document.querySelector('[data-entries-number-form-submit]')
    entriesNumberSubmit.addEventListener('click', () => {
        entriesNumberSubmit.querySelector('img').classList.add('rotate-animation')
    })

  
    new CreateEntry({ fieldName: 'taxa' })

    new Modal({
        modalContent: document.querySelector('[data-modal="group-action"]'),
        modalTrigger: document.querySelector('[data-open-modal="group-action"]'),
        modalClose: document.querySelector('[data-close-modal="group-action"]')
    })

    let fieldStatusAll = document.querySelectorAll('[data-field-action]')
    fieldStatusAll.forEach(fieldStatus => {
        const fieldWrapper = fieldStatus.nextElementSibling

        fieldStatus.addEventListener('change', (e) => {
            if (e.target.value == 'maintain') {
                fieldWrapper.classList.add('hide-div')
            } else {
                fieldWrapper.classList.remove('hide-div')
            }
        })
    })

    sync_location_fields(true)

    const moreFieldsButton = document.querySelector('[data-more-fields-button]')
    moreFieldsButton.addEventListener('click', () => {
        const moreFieldsDiv = moreFieldsButton.nextElementSibling
        
        const moreFieldsState = moreFieldsButton.dataset.state

        if (moreFieldsState == 'close') {
            moreFieldsDiv.style.display = 'flex'
            
            moreFieldsButton.setAttribute('data-state', 'open')
        }
        else {
            moreFieldsDiv.style.display = ''

            moreFieldsButton.setAttribute('data-state', 'close')
        }
    })
})()