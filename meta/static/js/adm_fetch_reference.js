(() => {
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
      referenceData.slug = data.DOI.toLowerCase()
      referenceData.citation = formattedCitation
      referenceData.doi = data.DOI
      referenceData.metadata = data
    }

    const displayNotFound = () => {
      result.innerHTML = ''
              
      const paragraph = document.createElement('p')
      paragraph.innerText = 'Referência não encontrada'
      result.append(paragraph)
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
    const result = document.querySelector('[data-result="doi"]')
    const doiSubmit = document.querySelector('[data-submit="doi"]')

    doiForm.addEventListener('submit', (e) => {
      e.preventDefault()
      result.innerHTML = ''

      const formData = new FormData(e.target)

      const isValid = validateDoi(formData.get('doi-input'))
      if (!isValid) return

      result.innerHTML = 'Carregando...'

      fetch(`https://api.crossref.org/works/${formData.get('doi-input')}`)
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
      console.log('Enviar requisição')
    })
})()