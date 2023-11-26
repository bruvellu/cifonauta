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
