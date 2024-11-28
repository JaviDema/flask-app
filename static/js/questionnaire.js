document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('questionnaireForm');
    const sections = document.querySelectorAll('.questionnaire-section');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const progressBar = document.getElementById('progressBar');
    
    let currentSection = 0;
    
    function showSection(index) {
        if (!sections || !sections.length) return;
        
        sections.forEach((section, i) => {
            if (section) {
                section.style.display = i === index ? 'block' : 'none';
            }
        });
        
        // Update buttons
        if (prevBtn) {
            prevBtn.style.display = index === 0 ? 'none' : 'block';
        }
        if (nextBtn) {
            nextBtn.style.display = index === sections.length - 1 ? 'none' : 'block';
        }
        if (submitBtn) {
            submitBtn.style.display = index === sections.length - 1 ? 'block' : 'none';
        }
        
        // Update progress bar
        if (progressBar) {
            const progress = ((index + 1) / sections.length) * 100;
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${Math.round(progress)}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        currentSection = index;
    }
    
    function validateSection(index) {
        if (!sections || !sections[index]) return false;
        
        const section = sections[index];
        const inputs = section.querySelectorAll('input[type="radio"]');
        const groups = new Set();
        inputs.forEach(input => groups.add(input.name));
        
        for (const group of groups) {
            if (!section.querySelector(`input[name="${group}"]:checked`)) {
                alert('Por favor, responde todas las preguntas de esta sección.');
                return false;
            }
        }
        return true;
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentSection > 0) {
                showSection(currentSection - 1);
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (validateSection(currentSection)) {
                showSection(currentSection + 1);
            }
        });
    }
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validateSection(currentSection)) {
                return;
            }
            
            const formData = {
                study_time: form.querySelector('input[name="study_time"]:checked')?.value,
                session_duration: form.querySelector('input[name="session_duration"]:checked')?.value,
                learning_pace: form.querySelector('input[name="learning_pace"]:checked')?.value,
                learning_style: form.querySelector('input[name="learning_style"]:checked')?.value,
                content_format: form.querySelector('input[name="content_format"]:checked')?.value,
                feedback_preference: form.querySelector('input[name="feedback_preference"]:checked')?.value,
                learning_goals: form.querySelector('input[name="learning_goals"]:checked')?.value,
                motivators: form.querySelector('input[name="motivators"]:checked')?.value,
                challenges: form.querySelector('input[name="challenges"]:checked')?.value,
                interest_areas: form.querySelector('input[name="interest_areas"]:checked')?.value,
                experience_level: form.querySelector('input[name="experience_level"]:checked')?.value,
                learning_tools: form.querySelector('input[name="learning_tools"]:checked')?.value
            };
            
            submitQuestionnaire(formData);
        });
    }
    
    // Show initial section
    if (sections && sections.length > 0) {
        showSection(0);
    }
});

function submitQuestionnaire(formData) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('No se encontró el token de autorización. Por favor, inicie sesión nuevamente.');
        window.location.href = '/';
        return;
    }

    fetch('/submit_questionnaire', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.user_type) {
            alert('Cuestionario enviado exitosamente. Tu perfil de aprendizaje ha sido identificado.');
            window.location.href = '/dashboard';
        } else {
            throw new Error(data.message || 'Error desconocido');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error al enviar el cuestionario: ' + error.message);
        if (error.message.includes('401')) {
            window.location.href = '/';
        }
    });
}
