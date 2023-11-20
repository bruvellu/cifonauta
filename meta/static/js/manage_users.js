function setUsersData(users) {
  usersData = users
  usersData = [
    {
      "curatorship_ids": ["36"],
      "id": "78",
      "name": "LiamAdmin"
    },
    {
      "curatorship_ids": ["36", "37"],
      "id": "27",
      "name": "OliviaAdmin"
    },
    {
      "curatorship_ids": ["36"],
      "id": "14",
      "name": "NoahAdmin"
    },
    {
      "curatorship_ids": ["36", "37"],
      "id": "83",
      "name": "AvaAdmin"
    },
    {
      "curatorship_ids": ["36"],
      "id": "32",
      "name": "EmmaAdmin"
    },
  ]

  usersData.sort((a, b) => a.name.localeCompare(b.name));
  console.log(usersData)
  changeCuratorship(curatorshipOptions.value)
}

function resetSearchInput(inputTag, optionsTag) {
  let spanVisible = inputTag.parentNode.querySelector('span')

  if (spanVisible) {
    spanVisible.remove()
  }

  inputTag.value = ''
  searchUsers(inputTag, optionsTag)

  let notFoundMessage = optionsTag.querySelector('[data-not-found]')

  if (notFoundMessage) {
    notFoundMessage.remove()
  }
}

function selectUser(buttonTag) {
  buttonTag.setAttribute('onclick', 'removeUser(this)')
  buttonTag.innerText = 'Remover'
  buttonTag.classList.remove('select-user-button')
  buttonTag.classList.add('remove-user-button')

  let input = document.createElement('input')
  input.setAttribute('type', 'text')
  input.setAttribute('name', 'specialist_ids')
  input.setAttribute('value', buttonTag.parentNode.getAttribute('value'))
  input.hidden = true
  buttonTag.insertAdjacentElement('afterend', input);

  let userName = buttonTag.previousElementSibling.innerText

  for (let selectedUser of selectedUsers.children) {
    if (selectedUser.querySelector('.user-name').innerText > userName) {
      selectedUsers.insertBefore(buttonTag.parentNode, selectedUser)
      return
    }
  }

  selectedUsers.append(buttonTag.parentNode)
}

function removeUser(buttonTag) {
  buttonTag.setAttribute('onclick', 'selectUser(this)')
  buttonTag.innerText = 'Adicionar'
  buttonTag.classList.remove('remove-user-button')
  buttonTag.classList.add('select-user-button')

  buttonTag.nextElementSibling.remove()

  let userName = buttonTag.previousElementSibling.innerText

  for (let userOption of userOptions.children) {
    if (userOption.querySelector('.user-name')?.innerText > userName) {
      userOptions.insertBefore(buttonTag.parentNode, userOption)
      return
    }
  }

  userOptions.append(buttonTag.parentNode)
}

function selectAllUsers() {
  let userOptionsArray = Array.from(userOptions.children)
  userOptionsArray.forEach(user => {
    if (!user.classList.contains('hide-div')) {
      let button = user.querySelector('.select-user-button')
      selectUser(button)
    }
  })

  resetSearchInput(searchUserOptions, userOptions)
  resetSearchInput(searchUsersInCuratorship, selectedUsers)
}

function removeAllUsers() {
  let selectedUsersArray = Array.from(selectedUsers.children)
  selectedUsersArray.forEach(user => {
    if (!user.classList.contains('hide-div')) {
      let button = user.querySelector('.remove-user-button')
      removeUser(button)
    }
  })

  resetSearchInput(searchUserOptions, userOptions)
  resetSearchInput(searchUsersInCuratorship, selectedUsers)
}

function changeCuratorship(curatorshipId) {
  selectedUsers.innerHTML = ''
  userOptions.innerHTML = ''

  usersData.forEach(user => {
    if (user.curatorship_ids.includes(curatorshipId)) {
      let html = `
      <div value=${user.id} class="selected-user">
          <span class="user-name">
            ${user.name}
          </span>
          <button class="remove-user-button" type="button" onclick="removeUser(this)">Remover</button>
          <input type="text" name="specialist_ids" value="${user.id}" hidden="">
      </div>
      `
      selectedUsers.innerHTML += html
    } else {
      let html = `
      <div value=${user.id} class="user-option">
          <span class="user-name">
            ${user.name}
          </span>
          <button class="select-user-button" type="button" onclick="selectUser(this)">Adicionar</button>
      </div>
      `
      userOptions.innerHTML += html
    }
  })
}

function searchUsers(inputTag, optionsTag) {
  let inputValue = inputTag.value.toLowerCase()
  let spanVisible = inputTag.parentNode.querySelector('span')

  if (inputValue != '' && !spanVisible) {
    let span = document.createElement('span')
    span.innerText = 'x'
    span.addEventListener('click', () => {
      inputTag.value = ''
      searchUsers(inputTag, optionsTag)
      span.remove()
    })

    inputTag.parentNode.insertBefore(span, inputTag)
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

  // let areAllUsersHidden = optionsArray.every(option => option.classList.contains('hide-div'))
  // let notFoundMessage = optionsTag.querySelector('[data-not-found]')
  // if (areAllUsersHidden && !notFoundMessage) {
  //   let span = document.createElement('span')
  //   span.setAttribute('data-not-found', '')
  //   span.innerText = 'Nenhum usuário encontrado'
  //   optionsTag.append(span)
  // } else if (!areAllUsersHidden && notFoundMessage) {
  //   notFoundMessage?.remove()
  // }
}


let usersData = []
const url = window.location.origin
fetch(`${url}/get-users`, {
  method: 'GET'
})
.then(response => {
  if (response.ok) {
    return response.json()
  }
})
.then(data => {
  if (data) {
    setUsersData(data.users)
  }
})

let selectedUsers = document.querySelector('#selected-users')
let userOptions = document.querySelector('#user-options')
let curatorshipOptions = document.querySelector('#id_curatorship')
let userOptionsList = document.querySelectorAll('.user-option')
let searchUserOptions = document.querySelector('#search-user-options')
let searchUsersInCuratorship = document.querySelector('#search-users-in-curatorship')
let searchUserAuthors = document.querySelector('#search-user-authors')
let usersTableForm = document.querySelector('.users-table-form')
let tableBody = document.querySelector('.table-body')


curatorshipOptions.addEventListener('change', () => {
  changeCuratorship(curatorshipOptions.value)
})
searchUserOptions.addEventListener('input', (e) => {
  searchUsers(searchUserOptions, userOptions)
})
searchUsersInCuratorship.addEventListener('input', (e) => {
  searchUsers(searchUsersInCuratorship, selectedUsers)
})

searchUserAuthors.addEventListener('input', (e) => {
  searchUsers(e.target, tableBody)
})