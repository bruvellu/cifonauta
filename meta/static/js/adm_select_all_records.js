const selectAllRecords = document.querySelector('#select-all-records')
const selectedRecordList = document.querySelectorAll('.selected-record')

selectAllRecords.addEventListener('click', () => {
  selectedRecordList.forEach(record => {
    if (selectAllRecords.checked) {
      record.checked = true
    } else {
      record.checked = false
    }
  })
})
