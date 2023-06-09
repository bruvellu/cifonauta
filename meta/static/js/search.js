function showCheckboxOptions(htmlTag, event) {
    event.preventDefault()
    let checkboxOptionsDiv = htmlTag.nextElementSibling
    let dropdownArrow = htmlTag.children[1]
    let displayBottom = document.querySelector('#display-bottom')
    let divDisplayValue = window.getComputedStyle(checkboxOptionsDiv).display
    console.log(divDisplayValue)
    if (divDisplayValue == 'none') {
        checkboxOptionsDiv.style.display = 'block'
        dropdownArrow.style.rotate = '90deg'
        displayBottom.style.display = 'block'
    }
    else {
        checkboxOptionsDiv.style.display = 'none'
        dropdownArrow.style.rotate = '0deg'
        displayBottom.style.display = 'none'
    }

    
}