/**
 * This script is responsible for handling the login form submission on a webpage. 
 * It captures the user's email and password, submits these credentials to a server for 
 * authentication, and handles the server's response to either redirect the user upon 
 * successful login or display error messages for login failure.
 *
 * Overview:
 * 1. An event listener is added to the 'loginForm' element, specifically listening for 
 *    the 'submit' event. This ensures the custom login logic is executed when the form 
 *    is submitted.
 * 2. The default form submission behavior is prevented using `e.preventDefault()` to 
 *    allow for custom validation and submission via JavaScript.
 * 3. The user's email and password are retrieved from the form's input fields.
 * 4. A POST request is made to the server's login endpoint using the fetch API. This 
 *    request includes the user's email and password as a JSON payload.
 * 5. Upon receiving a response from the server, the function first converts the response 
 *    to JSON format to facilitate easier data handling.
 * 6. The server's response is expected to include a message indicating successful login 
 *    or an error message detailing why the login failed.
 * 7. If the login is successful (indicated by the presence of a message in the response), 
 *    the user is redirected to the 'menu.html' page, signifying successful entry into the 
 *    protected area of the application.
 * 8. If the login fails, the server's error message is displayed to the user. This implementation 
 *    assumes the error message is specifically related to the email address and thus updates 
 *    the 'emailError' element's text content with the error message. This could be expanded or 
 *    adjusted depending on the expected error structure and UI design considerations.
 * 9. In the event of a network or unexpected error during the fetch operation, the catch block 
 *    logs the error to the console. Additional user-facing error handling could be implemented 
 *    here for a better user experience.
 *
 * This script demonstrates practical use of asynchronous JavaScript for form submission, 
 * including client-side form handling, communication with server-side authentication endpoints, 
 * and dynamic update of the webpage based on server response.
 */

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            window.location.href = 'menu.html'; // Redirect upon successful login
        } else {
            // Display the specific error message from the server
            document.getElementById('emailError').textContent = data.error;
            // Considering using a separate div for general error messages if it doesn't relate specifically to email
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
