document.getElementById('signOut').addEventListener('click', function() {
    // Clear authentication tokens or session information
    localStorage.removeItem('userToken'); // Adjust according to how you're storing tokens

    // Redirect to index.html
    window.location.href = 'index.html';
});
