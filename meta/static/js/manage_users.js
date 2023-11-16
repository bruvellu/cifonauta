function setCuratorshipData(data) {
  curatorshipData = data
}

function selectUser(userTag) {
  userTag.setAttribute('onclick', 'removeUser(this)')
  userTag.innerText = 'Remover'
  selectedUsers.append(userTag.parentNode)
}

function removeUser(userTag) {
  userTag.setAttribute('onclick', 'selectUser(this)')
  userTag.innerText = 'Adicionar'
  userOptions.append(userTag.parentNode)
}

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
    setCuratorshipData(data)
  }
})

console.log(curatorshipData)


let selectedUsers = document.querySelector('#selected-users')
let userOptions = document.querySelector('#user-options')
let curatorshipOptions = document.querySelector('#curatorship-options')

let userOptionsList = document.querySelectorAll('.user-option')