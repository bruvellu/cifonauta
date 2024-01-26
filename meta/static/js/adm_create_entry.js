class CreateEntry {
  constructor({ fieldName }) {
      this.fieldSelect = document.querySelector(`#id_${fieldName}`)
      this.fieldModalDiv = document.querySelector(`[data-modal="${fieldName}"]`)
      this.fieldForm = this.fieldModalDiv.querySelector(`[data-form="${fieldName}"]`)
      this.nameInput = this.fieldForm.querySelector(`[name="name"]`)
      this.formSubmitter = this.fieldForm.querySelector(`[data-submitter="${fieldName}"]`)
      this.responseMessage = this.fieldModalDiv.querySelector(`[data-response-message]`)
      this.fieldName = fieldName

      this.initModal()
      this.initEventListeners()
  }

  initModal() {
      this.modalClass = new Modal({
          modalContent: this.fieldModalDiv,
          modalTrigger: document.querySelector(`[data-open-modal="${this.fieldName}"]`),
          modalClose: this.fieldModalDiv.querySelector(`[data-close-modal="${this.fieldName}"]`),
          onCloseCallback: this.clearFields.bind(this)
      })
  }

  initEventListeners() {
      this.nameInput.addEventListener('input', () => {
          this.formSubmitter.disabled = false
      });

      this.fieldForm.addEventListener('submit', this.onSubmit.bind(this))
  }

  async onSubmit(event) {
      event.preventDefault()
      if (this.formSubmitter.disabled) return

      this.responseMessage.innerHTML = ''

      if (this.nameInput.value === '') {
          return this.onError('O campo não pode ser vazio');
      }

      this.formSubmitter.disabled = true

      const response = await fetch(`${window.location.origin}/api/${this.fieldName}/`, {
          method: 'POST',
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'X-CSRFToken': this.getCookie('csrftoken')
          },
          body: JSON.stringify({ name: this.nameInput.value })
      })

      try {
          if (!response.ok) {
              if (response.status === 409) {
                  const error = await response.json()
                  throw new Error(error)
              }

              throw new Error('Ocorreu um erro')
          }

          const data = await response.json()
          this.onSuccess(data)
      } catch (error) {
          this.onError(error.message)
      }
  }

  onSuccess(responseData) {
      const { message, data } = responseData

      const option = document.createElement('option')
      option.value = data.id
      option.innerText = data.name
      option.selected = true
      this.fieldSelect.append(option)

      this.modalClass.closeModal()
  }

  onError(message) {
      const p = document.createElement('p')
      p.innerText = message
      p.classList.add('response-error')

      this.responseMessage.append(p)
  }

  clearFields() {
      this.nameInput.value = ''
      this.responseMessage.innerHTML = ''
      this.formSubmitter.disabled = false
  }

  getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = jQuery.trim(cookies[i]);
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
}