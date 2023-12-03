let notAuthorsOptions = document.querySelector('#not-authors-options')
let searchNotAuthors = document.querySelector('#search-not-authors')
let selectedAuthors = document.querySelector('#selected-authors')
let searchAuthors = document.querySelector('#search-authors')
let selectAllAuthors = document.querySelector('#select-all-authors')
let removeAllAuthors = document.querySelector('#remove-all-authors')

let enableAuthors = new TwoTables(
  notAuthorsOptions,
  searchNotAuthors,
  selectedAuthors,
  searchAuthors,
  selectAllAuthors,
  removeAllAuthors
)

users = JSON.parse(document.querySelector('#users-json').textContent)

const divideAuthors = (data) => {
  let authors = data.filter(user => user.is_author)
  let notAuthors = data.filter(user => !user.is_author)

  return [authors, notAuthors]
}

enableAuthors.setData(users, 'author_ids', divideAuthors)



let selectedUsers = document.querySelector('#selected-users')
let userOptions = document.querySelector('#user-options')
let curatorshipOptions = document.querySelector('#id_curatorship')
let userOptionsList = document.querySelectorAll('.user-option')
let searchUserOptions = document.querySelector('#search-user-options')
let searchUsersInCuratorship = document.querySelector('#search-users-in-curatorship')
let selectAllUsers = document.querySelector('#select-all-users')
let removeAllUsers = document.querySelector('#remove-all-users')

let enableSpecialists = new TwoTables(
  userOptions, 
  searchUserOptions, 
  selectedUsers, 
  searchUsersInCuratorship, 
  selectAllUsers, 
  removeAllUsers, 
  curatorshipOptions
)

authors = JSON.parse(document.querySelector('#authors-json').textContent)

enableSpecialists.setData(authors, 'specialist_ids')