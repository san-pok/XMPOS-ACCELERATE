

// Function to validate email format
function validateEmail(email) {
    const regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return regex.test(email);
}

// Function to validate password complexity
function validatePassword(password) {   
    const isLongEnough = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    if (!isLongEnough) {
        return { valid: false, message: 'Password must be at least 8 characters long.' };
    } else if (!hasUppercase) {
        return { valid: false, message: 'Password must have uppercase characters.' };
    } else if (!hasSpecialChar) {
        return { valid: false, message: 'Password must contain at least one special character.' };
    } else {
        return { valid: true, message: '' };
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");

    document.getElementById('signupForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        document.getElementById('emailError').textContent = '';
        document.getElementById('passwordError').textContent = '';

        if (!validateEmail(email)) {
            document.getElementById('emailError').textContent = 'Please enter a valid email address.';
            return;
        }

        const passwordValidation = validatePassword(password);
        if (!passwordValidation.valid) {
            document.getElementById('passwordError').textContent = passwordValidation.message;
            return;
        }

        fetch('http://127.0.0.1:5000/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            document.getElementById('verificationSection').style.display = 'block';
            document.getElementById('signupForm').style.display = 'none';
            localStorage.setItem('userEmail', email); // Store email for later use
        })
        .catch((error) => {
            console.error('Error:', error);
            document.getElementById('emailError').textContent = error.error || 'An error occurred, please try again.';
        });
    });

    document.getElementById('verificationForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const email = localStorage.getItem('userEmail');
        const code = document.getElementById('verificationCode').value;

        fetch('http://127.0.0.1:5000/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, code: code })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            console.log('Verification Success:', data);
            window.location.href = '/login.html'; // Redirect to login page on successful verification
        })
        .catch((error) => {
            console.error('Verification Error:', error);
            document.getElementById('verificationCodeError').textContent = 'Verification failed, please try again.';
        });
    });
});
