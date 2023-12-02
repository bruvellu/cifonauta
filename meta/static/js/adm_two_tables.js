class TwoTables {
  data = []
  options
  searchOptions
  selectedOptions
  searchSelectedOptions
  selectAllOptions
  removeAllOptions
  categoryOptions
  selectedOptionsName

  constructor(options, searchOptions, selectedOptions, searchSelectedOptions, selectAllOptions, removeAllOptions, categoryOptions = null) {
    this.options = options
    this.searchOptions = searchOptions
    this.selectedOptions = selectedOptions
    this.searchSelectedOptions = searchSelectedOptions
    this.selectAllOptions = selectAllOptions
    this.removeAllOptions = removeAllOptions

    this.searchOptions.addEventListener('input', (e) => {
      this.searchOptions(this.searchOptions, this.options)
    })

    this.searchSelectedOptions.addEventListener('input', (e) => {
      this.searchOptions(this.searchSelectedOptions, this.selectedOptions)
    })

    this.selectAllOptions.addEventListener('click', () => {
      this.selectAll()
    })

    this.removeAllOptions.addEventListener('click', () => {
      this.removeAll()
    })

    if (categoryOptions != null) {
      this.categoryOptions = categoryOptions

      this.categoryOptions.addEventListener('change', (e) => {
        this.changeCategory(e.target.value)
      })
    } 
  }

  setData(data, name, customDivider) {
    this.data = data
    this.selectedOptionsName = name
  
    this.data.sort((a, b) => a.name.localeCompare(b.name))

    if (this.categoryOptions) {
      this.changeCategory(this.categoryOptions.value)
    } else {
      if (customDivider) {
        let [selected, notSelected] = customDivider(this.data)

        selected.forEach(item => {
          this.selectedOptions.append(this.createOptionTag(item, true))
        })

        notSelected.forEach(item => {
          this.options.append(this.createOptionTag(item, false))
        })
      }
    }
  }

  changeCategory(curatorshipId) {
    this.selectedOptions.innerHTML = ''
    this.options.innerHTML = ''
  
    this.data.forEach(user => {
      if (user.curatorship_ids.includes(curatorshipId)) {
        this.selectedOptions.append(this.createOptionTag(user, true))
      } else {
        this.options.append(this.createOptionTag(user, false))
      }
    })

    this.resetSearchInput(this.searchOptions, this.options)
    this.resetSearchInput(this.searchSelectedOptions, this.selectedOptions)
  }
  
  selectOption(buttonTag) {
    buttonTag.removeEventListener('click', this.clickHandler)
    buttonTag.addEventListener('click', () => {
      this.removeOption(buttonTag)
    })
    buttonTag.innerText = 'Remover'
    buttonTag.classList.remove('select-user-button')
    buttonTag.classList.add('remove-user-button')
  
    let input = document.createElement('input')
    input.setAttribute('type', 'text')
    input.setAttribute('name', this.selectedOptionsName)
    input.setAttribute('value', buttonTag.parentNode.getAttribute('value'))
    input.hidden = true
    buttonTag.insertAdjacentElement('afterend', input);
  
    let userName = buttonTag.previousElementSibling.innerText
  
    for (let selectedOption of this.selectedOptions.children) {
      if (selectedOption.querySelector('.user-name').innerText > userName) {
        this.selectedOptions.insertBefore(buttonTag.parentNode, selectedOption)
        return
      }
    }
  
    this.selectedOptions.append(buttonTag.parentNode)
  }
  
  removeOption(buttonTag) {
    buttonTag.removeEventListener('click', this.clickHandler)
    buttonTag.addEventListener('click', () => {
      this.selectOption(buttonTag)
    })
    buttonTag.innerText = 'Adicionar'
    buttonTag.classList.remove('remove-user-button')
    buttonTag.classList.add('select-user-button')
  
    buttonTag.nextElementSibling.remove()
  
    let userName = buttonTag.previousElementSibling.innerText
  
    for (let option of this.options.children) {
      if (option.querySelector('.user-name')?.innerText > userName) {
        this.options.insertBefore(buttonTag.parentNode, option)
        return
      }
    }
  
    this.options.append(buttonTag.parentNode)
  }
  
  selectAll() {
    let optionsArray = Array.from(this.options.children)
    optionsArray.forEach(option => {
      if (!option.classList.contains('hide-div')) {
        let button = option.querySelector('.select-user-button')
        this.selectOption(button)
      }
    })
  
    this.resetSearchInput(this.searchOptions, this.options)
    this.resetSearchInput(this.searchSelectedOptions, this.selectedOptions)
  }
  
  removeAll() {
    let selectedOptionsArray = Array.from(this.selectedOptions.children)
    selectedOptionsArray.forEach(option => {
      if (!option.classList.contains('hide-div')) {
        let button = option.querySelector('.remove-user-button')
        this.removeOption(button)
      }
    })
  
    this.resetSearchInput(this.searchOptions, this.options)
    this.resetSearchInput(this.searchSelectedOptions, this.selectedOptions)
  }

  createOptionTag(optionInfos, isSelected) {
    let div = document.createElement('div')
    div.setAttribute('value', optionInfos.id)
    isSelected ? div.classList.add('selected-user') : div.classList.add('user-option')

    let span = document.createElement('span')
    span.classList.add('user-name')
    span.innerText = optionInfos.name

    let button = document.createElement('button')
    button.setAttribute('type', 'button')
    isSelected ? button.classList.add('remove-user-button') : button.classList.add('select-user-button')
    isSelected ? button.innerText = 'Remover' : button.innerText = 'Adicionar'
    button.addEventListener('click', () => {
      isSelected ? this.removeOption(button) : this.selectOption(button)
    })

    let input = document.createElement('input')
    if (isSelected) {
      input.setAttribute('type', 'text')
      input.setAttribute('name', this.selectedOptionsName)
      input.setAttribute('value', optionInfos.id)
      input.hidden = true
    }

    div.append(span, button)

    if (isSelected) { div.append(input) }

    return div
  }
  
  searchOptions(inputTag, optionsTag) {
    let inputValue = inputTag.value.toLowerCase()
    let spanVisible = inputTag.parentNode.querySelector('button')
  
    if (inputValue != '' && !spanVisible) {
      let span = document.createElement('button')
      span.setAttribute('type', 'button')
      span.innerHTML = '&times;'
      span.addEventListener('click', () => {
        inputTag.value = ''
        this.searchOptions(inputTag, optionsTag)
        span.remove()
      })
  
      inputTag.insertAdjacentElement('afterend', span)
    }
  
    if (inputValue == '') {
      spanVisible?.remove()
    }
  
    let optionsArray = Array.from(optionsTag.children)
    optionsArray = optionsArray.filter(option => {
      let userName = option.querySelector('.user-name')?.innerText.toLowerCase()
      
      if (userName) {
        if (userName.includes(inputValue)) {
          option.classList.remove('hide-div')
        } else {
          option.classList.add('hide-div')
        }
        
        return option
      }
    })
  }

  resetSearchInput(inputTag, optionsTag) {
    let spanVisible = inputTag.parentNode.querySelector('span')
  
    if (spanVisible) {
      spanVisible.remove()
    }
  
    inputTag.value = ''
    this.searchOptions(inputTag, optionsTag)
  
    let notFoundMessage = optionsTag.querySelector('[data-not-found]')
  
    if (notFoundMessage) {
      notFoundMessage.remove()
    }
  }
}