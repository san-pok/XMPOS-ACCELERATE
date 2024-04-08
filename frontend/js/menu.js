
/**
 * This script is responsible for toggling the visual theme of the webpage between light and dark modes
 * and handling the sign-out process by removing the user's session or token information from localStorage.
 *
 * Theme Toggling:
 * 1. The theme toggler functionality is attached to an element with the class 'theme-toggler'.
 * 2. Upon clicking the 'theme-toggler' element, the script toggles the 'dark-theme-variables' class on the <body> tag.
 *    This class change is used to switch between light and dark themes using CSS variables.
 * 3. It also toggles the 'active' class on the first and second child <i> elements within the 'theme-toggler'.
 *    This is typically used to change the icon indicating the current theme (e.g., sun icon for light mode, moon icon for dark mode).
 *
 * Sign Out:
 * 1. Adds a click event listener to an element with the id 'signOut'.
 * 2. Upon clicking the 'signOut' button, the script removes the user's authentication token from localStorage.
 *    This step is crucial for securely ending the user's session.
 * 3. After removing the token, it redirects the user to 'index.html', effectively signing the user out.
 *    This redirection is a common practice to take users back to the homepage or login page after signing out.
 *
 * Usage:
 * - The theme toggling feature allows users to switch between light and dark modes for a more personalized
 *   or comfortable viewing experience, especially in different lighting conditions.
 * - The sign-out functionality ensures that users can securely end their session, removing any authentication
 *   tokens stored in the browser to prevent unauthorized access to their account.
 *
 * Implementation Notes:
 * - The actual storage and handling of 'userToken' should be adjusted according to the specific authentication
 *   mechanism in use. It's essential to securely manage authentication tokens to protect user data and privacy.
 * - The theme switcher relies on the presence of predefined CSS variables and classes to effectively change
 *   the theme. Ensure that your CSS is correctly set up to respond to these class changes for a seamless user experience.
 */
const themeToggler = document.querySelector(".theme-toggler");
themeToggler.addEventListener("click", ()=>{
    document.body.classList.toggle('dark-theme-variables')
  themeToggler.querySelector('i:nth-child(1)').classList.toggle('active');
  themeToggler.querySelector('i:nth-child(2)').classList.toggle('active');
})


document.getElementById('signOut').addEventListener('click', function() {
    // Clear authentication tokens or session information
    localStorage.removeItem('userToken'); // Adjust according to how you're storing tokens

    // Redirect to index.html
    window.location.href = 'index.html';
});


