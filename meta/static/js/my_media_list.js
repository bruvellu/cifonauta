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


    // let entriesNumberButton = document.querySelector('#entries-number-button')
    // entriesNumberButton.addEventListener('click', () => {
    //     entriesNumberButton.querySelector('img').classList.add('rotate-animation')
    // })


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
    console.log(moreFieldsButton)
    moreFieldsButton.addEventListener('click', () => {
        const dropdownArrow = moreFieldsButton.children[1]
        const moreFieldsDiv = moreFieldsButton.nextElementSibling
        
        const moreFieldsState = moreFieldsButton.dataset.state

        if (moreFieldsState == 'close') {
            moreFieldsDiv.style.display = 'flex'
            // dropdownArrow.style.rotate = '90deg'
            
            moreFieldsButton.setAttribute('data-state', 'open')

            // moreFieldsDiv.setAttribute('data-state', 'open')
            // dropdownArrow.setAttribute('data-state', 'open')
        }
        else {
            console.log('oi')
            moreFieldsDiv.style.display = ''
            moreFieldsDiv.style.removeProperty('display')

            moreFieldsButton.setAttribute('data-state', 'close')

            // moreFieldsDiv.setAttribute('data-state', 'close')
            // dropdownArrow.setAttribute('data-state', 'close')
        }
        
        // const moreFiltersButton = document.querySelector(".more-filters-button")
        // if (htmlTag.contains(moreFiltersButton)) {
        //     const displayBottom = document.querySelector('#display-bottom')
        //     const moreFilters = document.querySelector(".more-filters")
        //     const moreFiltersDisplay = window.getComputedStyle(moreFilters).display
        //     if (moreFiltersDisplay == 'none') {
        //         displayBottom.style.display = 'none'
        //     }
        //     else {
        //         displayBottom.style.display = 'block'
        //     }
        // }  
    })
})()