(() => {
    // Get cookie value by name (from Django docs)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Display message with results
    const displayResult = (message) => {
        result.innerHTML = '';
        const paragraph = document.createElement('p');
        paragraph.innerHTML = message;
        result.append(paragraph);
        doiSubmit.disabled = true;
    };

    // Handle successful reference addition
    const onSuccess = (data) => {
        result.innerHTML = '';
        const option = document.createElement('option');
        option.value = data.id;
        option.innerText = data.doi;
        option.selected = true;
        referenceSelect.append(option);
        clearReferenceData();
        doiSubmit.disabled = true;
        doiInput.value = '';
        referenceModal.closeModal(this);
    };

    // Validate DOI input
    const validateDoi = (doi) => {
	const regex = /^\d{2}\.\d{4,9}\/[a-zA-Z0-9\-._;()/:]+$/;
        const invalidDoi = doiForm.querySelector('[data-error="doi"]');
        invalidDoi?.remove();

        if (!regex.test(doi)) {
            const span = document.createElement('span');
            span.setAttribute('data-error', 'doi');
            span.classList.add('field__errors');
            span.innerText = 'Formato do DOI inválido';
            span.style.color = 'red';
            doiForm.append(span);
            doiSubmit.disabled = true;
            clearReferenceData();
            return false;
        }
        return true;
    };

    // Clear reference data
    const clearReferenceData = () => {
        referenceData.name = '';
        referenceData.citation = '';
        referenceData.doi = '';
    };

    // Object to store reference data
    let referenceData = {
        name: '',
        citation: '',
        doi: ''
    };

    // DOM element selections
    const doiForm = document.querySelector('[data-form="doi"]');
    const doiInput = document.querySelector('[data-input="doi"]');
    const result = document.querySelector('[data-result="doi"]');
    const doiSubmit = document.querySelector('[data-submit="doi"]');
    const referenceSelect = document.querySelector('#id_references');

    // Initialize modal
    const referenceModal = new Modal({
        modalContent: document.querySelector('[data-modal="references"]'),
        modalTrigger: document.querySelector('[data-open-modal="references"]'),
        modalClose: document.querySelector('[data-close-modal="references"]'),
        modalZIndex: 8
    });

    // Event listener for DOI form submission
    doiForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const isValid = validateDoi(doiInput.value);
        if (!isValid) return;
        
        result.innerHTML = 'Carregando...';
        const doi = doiInput.value;

        fetch(`https://doi.org/${doi}`, {
            headers: {
                'Accept': 'text/x-bibliography; style=apa',
            }
        })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        displayResult('Referência não encontrada');
                    }
                    throw new Error(response.statusText);
                }
                return response.text();
            })
            .then(data => {
                displayResult(data);
                doiSubmit.disabled = false;

                // Generate bibkey
                const lastName = data.match(/^([A-Za-z]+(?:[-\s][A-Za-z]+)*)/)[1];
                const pubYear = data.match(/\((\d{4})\)/)[1];
                const suffix = Array(2).fill().map(() => String.fromCharCode(97 + Math.floor(Math.random() * 26))).join('');
                let bibkey = `${lastName}${pubYear}-${suffix}`;
		bibkey = bibkey.replace(' ', '-')

                referenceData.name = bibkey;
                referenceData.citation = data;
                referenceData.doi = doi;
            })
            .catch(error => {
                clearReferenceData();
            });
    });

    // Event listener for DOI submission button
    doiSubmit.addEventListener('click', () => {
        if (referenceData.doi === '') {
            displayResult('Ocorreu um erro');
            return;
        }

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
                    if (response.status === 409) {
                        displayResult('Referência já existe no banco de dados');
                    }
                    throw new Error(response.statusText);
                }
                return response.json();
            })
            .then(data => {
                onSuccess(data);
            })
            .catch(error => {
                console.log(error);
            })
            .finally(() => clearReferenceData());
    });
})();
