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
