class CreateEntry {
  constructor({ fieldName }) {
    this.fieldSelect = document.querySelector(`#id_${fieldName}`);
    this.fieldModalDiv = document.querySelector(`[data-modal="${fieldName}"]`);
    this.fieldForm = this.fieldModalDiv.querySelector(`[data-form="${fieldName}"]`);
    this.nameInput = this.fieldForm.querySelector(`[name="name"]`);
    this.formSubmitter = this.fieldForm.querySelector(`[data-submitter="${fieldName}"]`);
    this.responseMessage = this.fieldModalDiv.querySelector(`[data-response-message]`);
    this.fieldName = fieldName;

    this.initModal();
    this.initEventListeners();
  }

  initModal() {
    this.modalClass = new Modal({
      modalContent: this.fieldModalDiv,
      modalTrigger: document.querySelector(`[data-open-modal="${this.fieldName}"]`),
      modalClose: this.fieldModalDiv.querySelector(`[data-close-modal="${this.fieldName}"]`),
      modalZIndex: 8,
      onCloseCallback: this.clearFields.bind(this)
    });
  }

  initEventListeners() {
    this.nameInput.addEventListener('input', () => {
      this.formSubmitter.disabled = false;
    });

    this.fieldForm.addEventListener('submit', this.onSubmit.bind(this));
  }

  async onSubmit(event) {
    event.preventDefault();
    if (this.formSubmitter.disabled) return;

    this.responseMessage.innerHTML = '';

    const name = this.nameInput.value.trim();

    if (!name) {
      return this.onError('O campo não pode ser vazio');
    }

    this.formSubmitter.disabled = true;

    try {
      const response = await fetch(`${window.location.origin}/api/${this.fieldName}/`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({ name: name })
      });

      const responseData = await response.json();

      if (!response.ok) {
        if (responseData.errors) {
          // Django Rest Framework - erros de validação do serializer
          const messages = Object.values(responseData.errors).flat().join('<br>');
          throw new Error(messages);
        } else {
          throw new Error(responseData.message || 'Ocorreu um erro desconhecido');
        }
      }

      this.onSuccess(responseData);
    } catch (error) {
      this.onError(error.message);
    }
  }

  onSuccess(responseData) {
    const { data } = responseData;

    const option = document.createElement('option');
    option.value = data.id;
    option.innerText = data.name;
    option.selected = true;
    this.fieldSelect.append(option);

    this.modalClass.closeModal();
  }

  onError(message) {
    const p = document.createElement('p');
    p.innerHTML = message;
    p.classList.add('response-error');

    this.responseMessage.innerHTML = '';
    this.responseMessage.append(p);
    this.formSubmitter.disabled = false;
  }

  clearFields() {
    this.nameInput.value = '';
    this.responseMessage.innerHTML = '';
    this.formSubmitter.disabled = false;
  }

  getCookie(name) {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith(name + '='))
      ?.split('=')[1];
    return cookieValue ? decodeURIComponent(cookieValue) : null;
  }
}
