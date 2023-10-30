function selectOption(event, htmlElem) {
  event.preventDefault()

  const instanceId = htmlElem.htmlFor.match(/\d+/)[0]

  if (!htmlElem.querySelector('input').checked) {
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
    removeBtn.setAttribute('onclick', `removeOption(${instanceId})`)
    removeBtn.setAttribute('value', instanceId)
    removeBtn.setAttribute('type', 'button')

    selectedOptionDiv.append(removeBtn)
    selectedOptionDiv.append(selectedOption)
    selectedOptions.append(selectedOptionDiv)

    
    saveInMediaField(instanceId)

  } else {
    removeOption(instanceId)
  }

  closeInputOptions()
  fakeInputSearch.focus()
}

function removeOption(id) {
  saveInMediaField(id)
  
  let selectedOption = selectedOptions.querySelector(`.id_media_${id}`)
  selectedOption.remove()

  let elemOption = fakeInputOptionsDiv.querySelector(`[value="${id}"]`)
  elemOption.checked = false
}

function saveInMediaField(id) {
  let options = Array.from(mediaField.options)
  let optionMedia = options.find(option => option.value == id)
  optionMedia.selected = !optionMedia.selected
}

function fetchToSearch() {
  const url = window.location.origin
  inputText = fakeInputSearch.value.toLowerCase()

  let loadingMessage
  if (!fetchLoading) {
    loadingMessage = document.createElement('span')
    loadingMessage.innerText = 'Carregando...'
    loadingMessage.setAttribute('id', 'fetch-loading')
    fetchLoading = true
    fakeInput.append(loadingMessage)
  }

  fetch(`${url}/get-tour-medias?input_value=${inputText}&offset=${offset}&limit=${limit}`, {
      method: "GET"
  })
  .then(response => {
    if (response.ok) {
      return response.json()
    }
  })
  .then(data => {
    offset += limit
    fakeInputOptionsDiv.innerHTML = ''

    if (data.medias?.length == 0) {
      let paragraph = document.createElement('p')
      paragraph.innerText = 'Mídia não encontrada'

      fakeInputOptionsDiv.append(paragraph)
    } else {
      loadOptions(data.medias)
    }
  })
  .finally(() => {
    loadingMessage.remove()
    if (fetchLoading) {
      fetchLoading = false
    }
  })
}

function fetchToLoadMore() {
  const url = window.location.origin

  inputText = fakeInputSearch.value.toLowerCase()

  let loadingMessage
  if (!fetchLoading) {
    loadingMessage = document.createElement('span')
    loadingMessage.innerText = 'Carregando...'
    loadingMessage.setAttribute('id', 'fetch-loading')
    fetchLoading = true
    fakeInput.append(loadingMessage)
  }

  fetch(`${url}/get-tour-medias?input_value=${inputText}&offset=${offset}&limit=${limit}`, {
      method: "GET"
  })
  .then(response => {
    if (response.ok) {
      return response.json()
    }
  })
  .then(data => {
    offset += limit
    loadOptions(data.medias)
  })
  .finally(() => {
    loadingMessage.remove()
    if (fetchLoading) {
      fetchLoading = false
    }
  })
}

function loadOptions(medias) {
  medias?.forEach(media => {
    let label = document.createElement('label')
    label.setAttribute('onclick', 'selectOption(event, this)')
    label.classList.add('fake-input-label')
    label.setAttribute('for', `id_media_${media.id}`)

    let input = document.createElement('input')
    const isOptionSelected = selectedOptions.querySelector(`[value="${media.id}"]`)
    input.checked = isOptionSelected ? true : false
    input.hidden = true
    input.setAttribute('class', 'input')
    input.setAttribute('type', 'checkbox')
    input.setAttribute('name', 'media2')
    input.setAttribute('value', media.id)
    label.setAttribute('id', `id_media_${media.id}`)

    let mediaType
    if (media.datatype == 'video') {
      mediaType = document.createElement('video')
    } else {
      mediaType = document.createElement('img')
    }
    mediaType.classList.add('tour-img', `size-${media.size}`)
    mediaType.setAttribute('src', media.coverpath)

    let tourInfosDiv = document.createElement('div')
    tourInfosDiv.setAttribute('class', 'tour-infos-div')

    let tourMediaLink = document.createElement('a')
    tourMediaLink.setAttribute('class', 'tour-media-link')
    //BOTAR O HREF
    tourMediaLink.setAttribute('href', '')
    tourMediaLink.setAttribute('target', '_blank')
    tourMediaLink.innerText = media.title

    let span = document.createElement('span')
    span.innerText = media.datatype == 'video' ? 'Vídeo' : 'Foto'

    tourInfosDiv.append(tourMediaLink, span)
    label.append(input, mediaType, tourInfosDiv)

    fakeInputOptionsDiv.append(label)
  })
  
}

function closeInputOptions() {
  fakeInputOptionsDiv.classList.add('hide-div')
  fakeInputSearch.value = ''
  isInputOptionsOpened = false
}

let fakeInputOptionsDiv = document.querySelector('.fake-input-options-div')
let fakeInput = document.querySelector('.fake-input')
let fakeInputSearch = document.querySelector('#fake-input-search')
let selectedOptions = document.querySelector('#selected-options')
let mediaOptions = document.querySelectorAll('.fake-input-label')
let mediaField = document.querySelector('#id_media')
mediaField.style.display = 'none'
let fetchLoading = false
let delayFetch
let offset = 20
let limit = 20

fakeInputSearch.addEventListener('input', () => {
  if (delayFetch) {
    clearTimeout(delayFetch);
  }

  offset = 0
  
  inputText = fakeInputSearch.value.toLowerCase()

  delayFetch = setTimeout(() => {
    if (inputText == '') {
      fetchToSearch()
    } else {
      fetchToSearch()
    }
  }, 300)
})


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

fakeInputOptionsDiv.addEventListener('scroll', () => {
  if (fakeInputOptionsDiv.scrollTop + fakeInputOptionsDiv.clientHeight >= fakeInputOptionsDiv.scrollHeight) {
    
    if (fakeInputSearch.value != '') {
      fetchToLoadMore(true)
    } else {
      fetchToLoadMore(true)
    }
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