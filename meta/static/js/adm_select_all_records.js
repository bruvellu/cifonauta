const selectAllRecords = document.querySelector('#select-all-records')
const selectedRecordAll = document.querySelectorAll('.selected-record')
let selectedRecordArray = Array.from(selectedRecordAll)

selectedRecordAll.forEach(record => {
  record.addEventListener('click', () => {
    const AllRecordsSelected = selectedRecordArray.every(record => record.checked)

    if (AllRecordsSelected) {
      selectAllRecords.checked = true
    } else {
      selectAllRecords.checked = false
    }
  })
})

selectAllRecords?.addEventListener('click', () => {
  if (selectAllRecords.checked) {
    selectedRecordAll.forEach(record => record.checked = true)
  } else {
    selectedRecordAll.forEach(record => record.checked = false)
  }
})
