let idTaxaAction = document.querySelector('#id_taxa_action')
let taxaWrapper = document.querySelector('#taxa-wrapper')
idTaxaAction.addEventListener('change', (e) => {
  console.log(idTaxaAction.value)
  if (idTaxaAction.value == 'maintain') {
    taxaWrapper.classList.add('hide-div')
  } else {
    taxaWrapper.classList.remove('hide-div')
  }
})