// const themeToggler =  document.querySelector(".theme-toggler");

// themeToggler.addEventListener('click', function (){
//     document.body.classList.toggle('dark-theme-variables')
//     themeToggler.querySelector('i:nth-child(1)').classList.toggle('active');
//     themeToggler.querySelector('i:nth-child(2)').classList.toggle('active');
// });

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


