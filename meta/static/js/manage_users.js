function setCuratorshipData(users) {
  usersData = users

  usersData.sort((a, b) => a.name.localeCompare(b.name));

  changeCuratorship(curatorshipOptions.value)
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
    if (userOption.querySelector('.user-name').innerText > userName) {
      userOptions.insertBefore(buttonTag.parentNode, userOption)
      return
    }
  }

  userOptions.append(buttonTag.parentNode)
}

function selectAllUsers() {
  selectedUsers.innerHTML = ''
  userOptions.innerHTML = ''

  usersData.forEach(user => {
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
  })
}

function removeAllUsers() {
  selectedUsers.innerHTML = ''
  userOptions.innerHTML = ''

  usersData.forEach(user => {
    let html = `
    <div value=${user.id} class="user-option">
        <span class="user-name">
          ${user.name}
        </span>
        <button class="select-user-button" type="button" onclick="selectUser(this)">Adicionar</button>
    </div>
    `
    userOptions.innerHTML += html
  })
}

function changeCuratorship(curatorshipId) {
  selectedUsers.innerHTML = ''
  userOptions.innerHTML = ''
  console.log(usersData)
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
    spanVisible.remove()
  }

  let optionsArray = Array.from(optionsTag.children)
  optionsArray.forEach(option => {
    let userName = option.querySelector('.user-name').innerText.toLowerCase()

    if (userName.includes(inputValue)) {
      option.classList.remove('hide-div')
    } else {
      option.classList.add('hide-div')
    }
  })
}

function searchUsersTable(inputValue) {
  inputValue = inputValue.toLowerCase()
  let tableSearchDiv = document.querySelector('.table-search-div')
  let spanVisible = tableSearchDiv.querySelector('span')

  if (inputValue != '' && !spanVisible) {
    let span = document.createElement('span')
    span.innerText = 'x'
    span.addEventListener('click', () => {
      searchUserAuthors.value = ''
      searchUsersTable(searchUserAuthors.value)
      span.remove()
    })

    tableSearchDiv.prepend(span)
  }

  if (inputValue == '') {
    spanVisible.remove()
  }

  let userRowArray = Array.from(document.querySelectorAll('.user-row'))
  userRowArray.forEach(user => {
    let userName = user.querySelector('.user-name-cedule').innerText.toLowerCase()

    if (userName.includes(inputValue)) {
      user.classList.remove('hide-div')
    } else {
      user.classList.add('hide-div')
    }
  })
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
    setCuratorshipData(data.users)
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
  searchUsersTable(e.target.value)
})