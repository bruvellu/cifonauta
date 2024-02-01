function closeOptionsContainer() {
  optionsContainer.classList.add('hide-div')
  searchOptionsInput.value = ''
  isOptionsContainerOpened = false

  if (optionsUl.querySelector('p')) {
    optionsUl.innerHTML = ''
    offset = 0
    fetchToSearch()
  }
}

function fetchToSearch() {
  const url = window.location.origin
  inputValue = searchOptionsInput.value.toLowerCase()

  let loadingMessage
  if (!fetchLoading) {
    loadingMessage = document.createElement('span')
    loadingMessage.innerText = 'Carregando...'
    loadingMessage.setAttribute('id', 'fetch-loading')
    fetchLoading = true
    inputContainer.append(loadingMessage)
  }

  fetch(`${url}/get-tour-medias?input_value=${inputValue}&offset=${offset}&limit=${limit}`, {
      method: "GET"
  })
  .then(response => {
    if (response.ok) {
      return response.json()
    }
  })
  .then(data => {
    offset += limit
    optionsUl.innerHTML = ''

    if (data.medias?.length == 0) {
      let paragraph = document.createElement('p')
      paragraph.innerText = 'Mídia não encontrada'

      optionsUl.append(paragraph)
    } else {
      optionsUl.scrollTop = 0
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

  inputValue = searchOptionsInput.value.toLowerCase()

  let loadingMessage
  if (!fetchLoading) {
    loadingMessage = document.createElement('span')
    loadingMessage.innerText = 'Carregando...'
    loadingMessage.setAttribute('id', 'fetch-loading')
    fetchLoading = true
    inputContainer.append(loadingMessage)
  }

  fetch(`${url}/get-tour-medias?input_value=${inputValue}&offset=${offset}&limit=${limit}`, {
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
    const isSelected = selectedMediaIds.has(media.id.toString())

    let li = document.createElement('li')
    li.id = `option_${media.id}`
    li.classList.add('media-option')
    console.log(isSelected)
    if (isSelected) {
      li.classList.add('media-option-selected')
    }
    li.setAttribute('onclick', 'selectOption(event, this)')

    let optionCover
    if (media.datatype == 'video') {
      optionCover = document.createElement('video')
    } else {
      optionCover = document.createElement('img')
    }
    optionCover.classList.add('option-cover', `scale-${media.scale}`)
    optionCover.setAttribute('src', media.coverpath)

    let optionInfos = document.createElement('div')
    optionInfos.setAttribute('class', 'option-infos')

    let optionTitle = document.createElement('a')
    optionTitle.setAttribute('class', 'option-title')
    optionTitle.setAttribute('href', media.coverpath)
    optionTitle.setAttribute('tabindex', '-1')
    optionTitle.setAttribute('target', '_blank')
    optionTitle.innerText = media.title

    let span = document.createElement('span')
    span.innerText = media.datatype == 'video' ? 'Vídeo' : 'Foto'

    optionInfos.append(optionTitle, span)
    li.append(optionCover, optionInfos)

    optionsUl.append(li)
  })
  
}

function selectOption(event, optionClicked) {
  event.preventDefault()

  const optionClickedId = optionClicked.id.match(/\d+/)[0]

  if (!selectedMediaIds.has(optionClickedId)) {
    selectedMediaIds.add(optionClickedId)
    optionClicked.classList.add('media-option-selected')

    let hiddenInput = document.createElement('input')
    hiddenInput.hidden = true
    hiddenInput.setAttribute('name', 'selected_media')
    hiddenInput.value = optionClickedId

    let selectedOption = document.createElement('div')
    selectedOption.classList.add('selected-option')
    selectedOption.id = `selected_${optionClickedId}`

    let removeBtn = document.createElement('button')
    removeBtn.classList.add('remove-selected-option-btn')
    removeBtn.setAttribute('onclick', `removeOption(${optionClickedId})`)
    removeBtn.setAttribute('value', optionClickedId)
    removeBtn.setAttribute('type', 'button')

    let optionInfosWrapper = document.createElement('div')
    optionInfosWrapper.classList.add('option-infos-wrapper')

    let optionCover = optionClicked.querySelector('.option-cover').cloneNode(true)
    let optionInfos = optionClicked.querySelector('.option-infos').cloneNode(true)
    let optionTitle = optionInfos.querySelector('.option-title')
    optionTitle.classList.remove('option-title')
    optionTitle.classList.add('selected-option-cover-link')

    selectedOption.append(hiddenInput, removeBtn)
    optionInfosWrapper.append(optionCover, optionInfos)
    selectedOption.append(optionInfosWrapper)

    selectedOptionsContainer.append(selectedOption)

  } else {
    removeOption(optionClickedId)
  }

  closeOptionsContainer()
  searchOptionsInput.focus()
}

function removeOption(id) {
  let selectedOption = selectedOptionsContainer.querySelector(`#selected_${id}`)
  selectedOption.remove()

  let option = optionsContainer.querySelector(`#option_${id}`)
  option?.classList.remove('media-option-selected')

  selectedMediaIds.delete(id.toString())

  if (selectedOptionsContainer.children.length == 0) {
    optionsUl.innerHTML = ''
    offset = 0
    searchOptionsInput.value = ''
    fetchToSearch()
  }
}



let inputContainer = document.querySelector('#input-container')
let selectedOptionsContainer = document.querySelector('#selected-options-container')
let searchOptionsInput = document.querySelector('#search-options-input')
let optionsContainer = document.querySelector('#options-container')
let optionsUl = document.querySelector('#options-ul')
let fetchLoading = false
let delayFetch
let offset = 0
let limit = 20
let isOptionsContainerOpened = false
let isTheFirstClickOnInput = true


// Get the IDs of the medias initially selected
let selectedMediaIds = new Set()
let selectedOptions = Array.from(selectedOptionsContainer.querySelectorAll('.selected-option'))
selectedOptions.forEach(selectedOption => {
  selectedMediaIds.add(selectedOption.id.match(/\d+/)[0]) // Getting the id in selected_7
})



inputContainer.addEventListener('click', () => {
  if (isTheFirstClickOnInput) {
    fetchToSearch()
    isTheFirstClickOnInput = false
  }
  isOptionsContainerOpened = true
  optionsContainer.classList.remove('hide-div')
  optionsContainer.scrollIntoView({ block: 'center'})
  searchOptionsInput.focus()
})

document.addEventListener('click', (event)=>{
  if (!optionsContainer.contains(event.target) && 
      !inputContainer.contains(event.target) &&
      isOptionsContainerOpened) {
        closeOptionsContainer()
  }
})

searchOptionsInput.addEventListener('input', () => {
  if (delayFetch) {
    clearTimeout(delayFetch);
  }

  offset = 0

  delayFetch = setTimeout(() => {
    fetchToSearch()
  }, 300)
})

optionsContainer.addEventListener('scroll', () => {
  if (optionsContainer.scrollHeight - optionsContainer.clientHeight <= optionsContainer.scrollTop + 1) {
    fetchToLoadMore()
  }
})
