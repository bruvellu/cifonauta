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


    const modals = document.querySelectorAll('[data-modal]')
    modals.forEach(modal => {
        const modalName = modal.dataset.modal
        
        new Modal({
            modalContent: document.querySelector(`[data-modal='${modalName}']`),
            modalTrigger: document.querySelector(`[data-open-modal='${modalName}']`),
            modalClose: document.querySelector(`[data-close-modal='${modalName}']`)
        })
    })


    const moreFieldsButton = document.querySelector('[data-more-fields-button]')
    moreFieldsButton.addEventListener('click', () => {
        const dropdownArrow = moreFieldsButton.children[1]
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