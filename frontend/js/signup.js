/**
 
 * Function: validateEmail
 * Purpose: Validates if the given email string follows the standard email format.
 * Parameters: 
   - email (String): The email address to validate.
 * Returns: 
   - (Boolean): True if the email matches the standard format, false otherwise.
 * Details:
   - Utilizes a regular expression (regex) to check if the email conforms to the general email syntax standards.
   - The regex checks for characters allowed in the user name part, the @ symbol, and the domain part.

 */

function validateEmail(email) {
    const regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return regex.test(email);
}


/**
 * 
* Function: validatePassword
* Purpose: Validates the complexity of a given password to ensure it meets security requirements.
* Parameters:
   - password (String): The password to validate.
* Returns: 
   - (Object): An object with a 'valid' key indicating true or false, and a 'message' key with details on the validation result.
* Details:
   - The function checks for three criteria: length of at least 8 characters, inclusion of at least one uppercase character, and at least one special character.
   - If the password fails any of these checks, the function returns an object indicating the failure reason. If all checks pass, it returns an object indicating the password is valid.

 */
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



/**
 * This script adds event listeners to the DOM for handling user interactions
 * with the signup and verification forms on a webpage. It ensures that the user's
 * input is validated before sending the data to a server. If the input validation
 * fails, it displays appropriate error messages. Upon successful signup and verification,
 * it updates the UI to reflect the state change and stores the user's email in localStorage.
 *
 * Overview:
 * 1. Adds a listener for the 'DOMContentLoaded' event to ensure the DOM is fully loaded
 *    before running the script.
 * 2. Sets up an event listener on the signup form to intercept the submit event, preventing
 *    the default form submission to validate the user's email and password input client-side.
 * 3. Validates the email using the validateEmail function and updates the UI with an error
 *    message if the validation fails.
 * 4. Validates the password using the validatePassword function and updates the UI with an
 *    error message if the validation fails.
 * 5. If both validations pass, it sends a POST request to a server endpoint to create a new
 *    user account, using the fetch API. The request body includes the user's email and password.
 * 6. Upon a successful response from the server, it hides the signup form, displays a verification
 *    section, and stores the user's email in localStorage for later use.
 * 7. If there's an error in the signup process, it displays an appropriate error message to the user.
 * 8. Sets up an event listener on the verification form to handle the submission of a verification code.
 * 9. Retrieves the user's email from localStorage and sends it along with the verification code to the server
 *    for verification.
 * 10. If the verification is successful, it redirects the user to the login page. Otherwise, it displays
 *     an error message asking the user to try the verification process again.
 *
 * This script demonstrates handling form submission and input validation in JavaScript,
 * making asynchronous requests with the fetch API, and managing UI state based on server responses.
 */

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
