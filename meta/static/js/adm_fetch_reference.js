(() => {
    function getCookie(name) {
        // Got this from django docs
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const displayDOIResponse = (data) => {
        const authors = data.author?.flatMap((author, index) => {
          return ` ${author.given}`
        })

        let pagesInfo = ''
        if (data.volume && data.issue && data.page) {
          pagesInfo = `${data.volume}(${data.issue}) ${data.page},`
        }

        const formattedCitation = `<strong>${data.published?.['date-parts']?.[0][0]}</strong>. ${authors ? `${authors}.` : ''}<em>${data.title?.[0]}</em>. ${data['container-title']?.[0]}, ${pagesInfo} doi: <a href=${data.URL}>${data.DOI}</a>`

        const paragraph = document.createElement('p')
        paragraph.innerHTML = formattedCitation

        const result = document.querySelector('[data-result="doi"]')
        result.innerHTML = ''
        result.append(paragraph)
        doiSubmit.disabled = false

        referenceData.name = data.DOI
        referenceData.slug = (Math.floor(Math.random() * 99999) + 1).toString()
        referenceData.citation = formattedCitation
        referenceData.doi = data.DOI
        referenceData.metadata = data
    }

    const displayNotFound = () => {
        result.innerHTML = ''
                
        const paragraph = document.createElement('p')
        paragraph.innerText = 'Referência não encontrada'
        result.append(paragraph)
        doiSubmit.disabled = true
    }

    const displayConflict = () => {
        result.innerHTML = ''
                
        const paragraph = document.createElement('p')
        paragraph.innerText = 'Referência já existe no banco de dados'
        result.append(paragraph)
        doiSubmit.disabled = true
    }

    const displaySuccess = (data) => {
        result.innerHTML = ''

        const option = document.createElement('option')
        option.value = data.id
        option.innerText = data.doi
        option.selected = true
        referenceSelect.append(option)

        clearReferenceData()
        doiSubmit.disabled = true
        doiInput.value = ''

        referenceModal.closeModal(this)
    }

    const validateDoi = (doi) => {
        const regex = /^\d{2}\.\d{4}\/(.+)$/
        
        const invalidDoi = doiForm.querySelector('[data-error="doi"]')
        invalidDoi?.remove()

        if (!regex.test(doi)) {
          const span = document.createElement('span')
          span.setAttribute('data-error', 'doi')
          span.classList.add('field-error')
          span.innerText = 'Formato do DOI inválido'
          span.style.color = 'red'
          doiForm.append(span)
          
          doiSubmit.disabled = true
          clearReferenceData()

          return false
      }

      return true
    }

    const clearReferenceData = () => {
        referenceData.name = ''
        referenceData.slug = ''
        referenceData.citation = ''
        referenceData.doi = ''
        referenceData.metadata = {}
    }

    let referenceData = {
        name: '',
        slug: '',
        citation: '',
        doi: '',
        metadata: {}
    }

    const doiForm = document.querySelector('[data-form="doi"]')
    const doiInput = document.querySelector('[data-input="doi"')
    const result = document.querySelector('[data-result="doi"]')
    const doiSubmit = document.querySelector('[data-submit="doi"]')
    const referenceSelect = document.querySelector('#id_references')
    const referenceModal = new Modal({
        modalContent: document.querySelector('[data-modal="references"]'),
        modalTrigger: document.querySelector('[data-open-modal="references"]'),
        modalClose: document.querySelector('[data-close-modal="references"]')
    })

    doiForm.addEventListener('submit', (e) => {
        e.preventDefault()
        result.innerHTML = ''

        const isValid = validateDoi(doiInput.value)
        if (!isValid) return

        result.innerHTML = 'Carregando...'

        fetch(`https://api.crossref.org/works/${doiInput.value}`)
            .then(response => {
              if (!response.ok) {
                if (response.status == 404) {
                  displayNotFound()
                }

                throw new Error(response.statusText)
              }

              return response.json()
            })
            .then(data => {
              displayDOIResponse(data.message)
            })
            .catch(error => {
              console.log(error)
              clearReferenceData()
            })
    })

    doiSubmit.addEventListener('click', () => {
        fetch(`${window.location.origin}/api/reference/`, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(referenceData)
        })
            .then(response => {
                if (!response.ok) {
                  if (response.status == 409) {
                    displayConflict()
                  }

                  throw new Error(response.statusText)
                }

                return response.json()
            })
            .then(data => {
                displaySuccess(data)
            })
            .catch(error => {
                console.log(error)
            })
            .finally(() => clearReferenceData())
    })
})()