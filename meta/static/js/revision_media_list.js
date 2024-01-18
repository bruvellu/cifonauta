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


    let entriesNumberButton = document.querySelector('#entries-number-button')
    entriesNumberButton?.addEventListener('click', () => {
        entriesNumberButton.querySelector('img').classList.add('rotate-animation')
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

})()