function showCheckboxOptions(htmlTag, event) {
    event.preventDefault()

    const dropdownArrow = htmlTag.children[1]
    const checkboxOptionsDiv = htmlTag.nextElementSibling
    const divDisplayValue = window.getComputedStyle(checkboxOptionsDiv).display
    if (divDisplayValue == 'none') {
        checkboxOptionsDiv.style.display = 'block'
        dropdownArrow.style.rotate = '90deg'
    }
    else {
        checkboxOptionsDiv.style.display = 'none'
        dropdownArrow.style.rotate = '0deg'
    }
    
    const moreFiltersButton = document.querySelector(".more-filters-button")
    if (htmlTag.contains(moreFiltersButton)) {
        const displayBottom = document.querySelector('#display-bottom')
        const moreFilters = document.querySelector(".more-filters")
        const moreFiltersDisplay = window.getComputedStyle(moreFilters).display
        if (moreFiltersDisplay == 'none') {
            displayBottom.style.display = 'none'
        }
        else {
            displayBottom.style.display = 'block'
        }
    }  
}

