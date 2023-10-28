function selectOption(event, htmlElem) {
  event.preventDefault()

  if (!htmlElem.querySelector('input').checked || pageJustLoaded) {
    htmlElem.querySelector('input').checked = true

    const tourImg = htmlElem.querySelector('.tour-img').cloneNode(true)
    let tourInfosDiv = htmlElem.querySelector('.tour-infos-div').cloneNode(true)
    tourInfosDiv.querySelector('a').classList.remove('tour-media-link')
    tourInfosDiv.querySelector('a').classList.add('selected-option-media-link')

    let selectedOption = document.createElement('div')
    selectedOption.classList.add('selected-option')
    selectedOption.append(tourImg)
    selectedOption.append(tourInfosDiv)

    let selectedOptionDiv = document.createElement('div')
    selectedOptionDiv.classList.add('selected-option-div', `${htmlElem.htmlFor}`)
  
    let removeBtn = document.createElement('button')
    removeBtn.classList.add('remove-selected-option-btn')
    removeBtn.addEventListener('click', () => {
        removeOption(htmlElem)
    })
    removeBtn.setAttribute('type', 'button')

    selectedOptionDiv.append(removeBtn)
    selectedOptionDiv.append(selectedOption)
    selectedOptions.append(selectedOptionDiv)
  } else {
    console.log('já estava selecionado')

    if (!pageJustLoaded) {
      removeOption(htmlElem)
    }
  }

  closeInputOptions()
  fakeInputSearch.focus()
}

function removeOption(elemOption) {
  console.log(selectedOptions.querySelector(`.${elemOption.htmlFor}`))
  selectedOptions.querySelector(`.${elemOption.htmlFor}`).remove()
  elemOption.querySelector('input').checked = false
}

function searchOptions() {
  mediaOptions.forEach(option => {
    optionTitle = option.querySelector('.tour-media-link').innerText.toLowerCase()
    inputText = fakeInputSearch.value.toLowerCase()

    if (optionTitle.includes(inputText)) {
      option.classList.remove('hide-div')
    } else {
      option.classList.add('hide-div')
    }
  })
}

function closeInputOptions() {
  fakeInputOptionsDiv.classList.add('hide-div')
  fakeInputSearch.value = ''
  searchOptions()
}

let fakeInputOptionsDiv = document.querySelector('.fake-input-options-div')
let fakeInput = document.querySelector('.fake-input')
let fakeInputSearch = document.querySelector('#fake-input-search')
let selectedOptions = document.querySelector('#selected-options')

let mediaOptions = document.querySelectorAll('.fake-input-label')

let pageJustLoaded = true
document.addEventListener('DOMContentLoaded', () => {
  mediaOptions.forEach(option => {
    if (option.querySelector('input').checked) {
      selectOption(event, option)
    }
  })
  pageJustLoaded = false
})

fakeInputSearch.addEventListener('input', searchOptions)

fakeInput.addEventListener('click', () => {
  isInputOptionsOpened = true
  fakeInputOptionsDiv.classList.remove('hide-div')
  fakeInputOptionsDiv.scrollIntoView({ block: 'center'})
  fakeInputSearch.focus()
})

let tourForm = document.querySelector('.tour-form')
tourForm.addEventListener('submit', (e) => {
  if (document.activeElement == fakeInputSearch) {
    e.preventDefault()
  }
})

let isInputOptionsOpened = false
document.addEventListener('click', (event)=>{
  if (!fakeInputOptionsDiv.contains(event.target) && 
      !fakeInput.contains(event.target) &&
      isInputOptionsOpened) {
          closeInputOptions()
  }
})