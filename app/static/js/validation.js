
// Formulario para las validaciones
Document.addEvenListener('DOMContentLoaded',()=>{
    const validateForm = (event) =>{
        let email = document.getElementById('email').value;
        let pass = document.getElementById('pass').value;
        let passConfirmation = document.getElementById('passwordConfirmation').value;
        let emailError = document.getElementById('error-message-email');
        let passError = document.getElementById('error-message-pass');
        let passConfirmError = document.getElementById('error-message-pass-c');
        let emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
        let isValid = true;  

        //Reset error Messages
        emailError.style.display = 'none';
        passError.style.display = 'none';
        passConfirmError.style.display = 'none';

        //Validate email format
        if(!emailRegex.test(email)){
            emailError.textContent = 'Correo electrónico inválido';
            emailError.style.display = 'none';
            isValid = false;         
        }
        // Validate password
        if (pass.length < 6) {
            passError.textContent = 'La contraseña debe tener al menos 6 caracteres';
            passError.style.display = 'block';
            isValid = false;
        }

        // Validate password confirmation
        if (pass !== passConfirmation) {
            passConfirmError.textContent = 'Las contraseñas no coinciden';
            passConfirmError.style.display = 'block';
            isValid = false;
        }
        if (!isValid) {
            event.preventDefault();
        }

        return isValid;
    }
    document.getElementById('miRegistro').onsubmit = validateForm;
});

