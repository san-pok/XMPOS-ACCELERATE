document.addEventListener('DOMContentLoaded', async function() {
    const form = document.getElementById('monolith-deployment-form');
    // Add event listener for form submission
    form.addEventListener('submit', async function(event) {
        try {
             // Prevent the default form submission behavior
            event.preventDefault();
            // Gather the form data
            const formData = new FormData(form);
            // Convert FormData to JSON object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            // alert(JSON.stringify(data));
            const message = 'EC2 instance is being created.....'
            alert(message);
            // updateStatusMessage(message);
            // Redirect to index.html with message as query parameter
            // window.location.href = '/index.html?message=' + encodeURIComponent(message);

            // Redirect to the main page
            window.location.href = '/';
          
            // Send the form data to the server
            
            const response = await fetch('/submit-form-monolith', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            
            // Reload the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1000); // Refresh after 1 seconds (adjust as needed)
        // // Redirect to the main page
        // window.location.href = '/';    

        } catch (error){
            console.error('Error on submitting forms for Monolith deployment ', error);
        }

    });

    // Function to update status message in index.html
    function updateStatusMessage(message) {
        //  id "statusMessage" in index.html
        alert('In the statusMessage');
        const statusMessageElement = document.getElementById('statusMessage');
        // document.getElementById('statusMessage').textContent = 'Destroying EC2 instance...';
        if (statusMessageElement) {
            alert('In the statusMessage');
             // Redirect to index.html with message as query parameter
            window.location.href = '/index.html?message=' + encodeURIComponent(message);
            statusMessageElement.textContent = message;
            // Displaying status message
        } else {
            console.error("Status message element not found in index.html");
        }
    }
});
 