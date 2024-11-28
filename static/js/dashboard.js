document.addEventListener('DOMContentLoaded', function() {
    loadUserProfile();
    setupChatInterface();
});

function loadUserProfile() {
    fetch('/get_user_profile', {
        method: 'GET',
        headers: {
            'Authorization': localStorage.getItem('token')
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('userEmail').textContent = data.email;
        document.getElementById('userType').textContent = data.user_type;
        
        // Add user type description
        const typeDescriptions = {
            'ESTRUCTURADO': 'Recibirás explicaciones detalladas y analíticas para maximizar tu aprendizaje.',
            'EXPLORADOR': 'Recibirás explicaciones balanceadas con ejemplos prácticos.',
            'INTENSIVO': 'Recibirás explicaciones claras y paso a paso con ejemplos cotidianos.'
        };
        const description = document.getElementById('userTypeDescription');
        description.innerHTML = `<p class="mt-2"><small class="text-muted">${typeDescriptions[data.user_type] || ''}</small></p>`;
    })
    .catch((error) => {
        showError('Error al cargar el perfil: ' + error.message);
    });
}

function setupChatInterface() {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    let currentFile = null;
    let lastChatId = null;

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            currentFile = e.target.files[0];
            fileName.textContent = currentFile.name;
            filePreview.style.display = 'block';
        }
    });

    removeFile.addEventListener('click', function() {
        currentFile = null;
        fileInput.value = '';
        filePreview.style.display = 'none';
    });

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message || currentFile) {
            sendMessage(message);
            messageInput.value = '';
        }
    });

    function createFeedbackButtons(chatId) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.classList.add('feedback-buttons', 'mt-2', 'mb-3');
        
        const helpfulBtn = document.createElement('button');
        helpfulBtn.classList.add('btn', 'btn-sm', 'btn-outline-success', 'me-2');
        helpfulBtn.innerHTML = '👍 Útil';
        helpfulBtn.onclick = () => submitFeedback(chatId, true);
        
        const notHelpfulBtn = document.createElement('button');
        notHelpfulBtn.classList.add('btn', 'btn-sm', 'btn-outline-danger', 'me-2');
        notHelpfulBtn.innerHTML = '👎 No útil';
        notHelpfulBtn.onclick = () => submitFeedback(chatId, false);
        
        const understandingDiv = document.createElement('div');
        understandingDiv.classList.add('mt-2');
        understandingDiv.innerHTML = '<small class="text-muted">¿Qué tan bien entendiste la respuesta?</small><br>';
        
        for (let i = 1; i <= 5; i++) {
            const levelBtn = document.createElement('button');
            levelBtn.classList.add('btn', 'btn-sm', 'btn-outline-secondary', 'me-1');
            levelBtn.textContent = i;
            levelBtn.onclick = () => submitUnderstanding(chatId, i);
            understandingDiv.appendChild(levelBtn);
        }
        
        feedbackDiv.appendChild(helpfulBtn);
        feedbackDiv.appendChild(notHelpfulBtn);
        feedbackDiv.appendChild(understandingDiv);
        
        return feedbackDiv;
    }

    function submitFeedback(chatId, helpful) {
        fetch('/chat_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': localStorage.getItem('token')
            },
            body: JSON.stringify({
                chat_id: chatId,
                helpful: helpful
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            showSuccess('¡Gracias por tu feedback!');
        })
        .catch(error => {
            showError('Error al enviar feedback: ' + error.message);
        });
    }

    function submitUnderstanding(chatId, level) {
        fetch('/chat_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': localStorage.getItem('token')
            },
            body: JSON.stringify({
                chat_id: chatId,
                understanding: level
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            showSuccess('¡Gracias por indicar tu nivel de comprensión!');
        })
        .catch(error => {
            showError('Error al enviar nivel de comprensión: ' + error.message);
        });
    }

    function sendMessage(message) {
        messageInput.disabled = true;
        sendButton.disabled = true;
        sendButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';

        displayMessage(message, 'user-message');

        const formData = new FormData();
        if (message) formData.append('message', message);
        if (currentFile) formData.append('file', currentFile);

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Authorization': localStorage.getItem('token')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayMessage(data.response, 'ai-message');
            lastChatId = data.chat_id;
            
            if (lastChatId) {
                const feedbackButtons = createFeedbackButtons(lastChatId);
                chatMessages.appendChild(feedbackButtons);
            }
        })
        .catch((error) => {
            showError('Error: ' + error.message);
            displayMessage('Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta nuevamente.', 'error-message');
        })
        .finally(() => {
            messageInput.disabled = false;
            sendButton.disabled = false;
            sendButton.innerHTML = 'Enviar';
            messageInput.focus();
            currentFile = null;
            fileInput.value = '';
            filePreview.style.display = 'none';
        });
    }

    function displayMessage(message, className) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', className, 'mb-2', 'p-2');
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function showError(message) {
    const errorToast = document.getElementById('errorToast');
    const errorBody = errorToast.querySelector('.toast-body');
    errorBody.textContent = message;
    const toast = new bootstrap.Toast(errorToast);
    toast.show();
}

function showSuccess(message) {
    const successToast = document.getElementById('successToast');
    if (!successToast) {
        const toastContainer = document.querySelector('.toast-container');
        const successToastHTML = `
            <div id="successToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-success text-white">
                    <strong class="me-auto">Éxito</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                </div>
                <div class="toast-body"></div>
            </div>
        `;
        toastContainer.insertAdjacentHTML('beforeend', successToastHTML);
    }
    
    const successToastElement = document.getElementById('successToast');
    const successBody = successToastElement.querySelector('.toast-body');
    successBody.textContent = message;
    const toast = new bootstrap.Toast(successToastElement);
    toast.show();
}
