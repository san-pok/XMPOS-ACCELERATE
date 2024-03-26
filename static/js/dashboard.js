document.addEventListener('DOMContentLoaded', async function() {
    const monolithDeploymentLink = document.getElementById('monolith-deployment');

    // document.getElementById('instanceCount').innerText = 'Calculating...'

    // Function to fetch instance count and update the UI
    function fetchLightsailInstanceCount() {
        // Show the loading spinner
        document.getElementById('loadingSpinner').style.display = 'inline-block';
        fetch('/count-lightsail-instances')
            .then(response => response.json())
            .then(data => {
                document.getElementById('lightsailInstanceCount').innerText = data.running_instances;
            })
            .catch(error => console.error('Error fetching instance count:', error))
            
            .finally(() => {
                // Hide the loading spinner regardless of the outcome
                document.getElementById('loadingSpinner').style.display = 'none';
            });
    }

    // Function to fetch instance count and update the UI
    function fetchMonolithInstanceCount() {
        // Show the loading spinner
        // document.getElementById('loadingSpinnerMono').style.display = 'inline-block';
        fetch('/monolith/count-running-ec2-instances')
            .then(response => response.json())
            .then(data => {
                document.getElementById('MonolithInstanceCount').innerText = data.running_instances;
            })
            .catch(error => console.error('Error fetching instance count:', error))
            
            .finally(() => {
                // Hide the loading spinner regardless of the outcome
                // document.getElementById('loadingSpinner').style.display = 'none';
            });
    }

    // Call the function when the page is loaded
    fetchLightsailInstanceCount();
    fetchMonolithInstanceCount();
    
    // if (monolithDeploymentLink) {
    //     monolithDeploymentLink.addEventListener('click', function(event) {
    //         event.preventDefault(); // Prevent the default behavior of the anchor tag

    //         // Load the input-monolith.html content dynamically
    //         fetch('/input-monolith') // Assuming the route is '/input-monolith'
    //             .then(response => response.text())
    //             .then(html => {
    //                 // Replace the content of the current page with input-monolith.html content
    //                 document.documentElement.innerHTML = html;
    //                 alert('input-monolith.html loaded successfully!');
    //                 // Insert the content of input-monolith.html into a container
    //                 document.getElementById('content-container').innerHTML = html;
    //                 // Now that the content is loaded, load the input-monolith.js file dynamically
    //                 const script = document.createElement('script');
    //                 script.src = '/static/js/input-monolith.js'; // Adjust the path if needed
    //                 document.body.appendChild(script);
    //             })
    //             .catch(error => console.error('Error loading input-monolith.html:', error));
    //     });
    // } else {
    //     console.error("Anchor tag with ID 'monolith-deployment' not found.");
    // }

    // if (monolithDeploymentLink) {
    //     monolithDeploymentLink.addEventListener('click', function(event){
    //         event.preventDefault(); // Prevent the default behavior of following the link
    //         window.location.href = '../static/input-monolith.html';
    //         // window.location.href = './static/lightsail-deployment.html';
    //     });
    // } else {
    //     console.error("Button with ID 'wordpressEc2Btn' not found.");
    // }



    document.addEventListener('DOMContentLoaded', function() {
        const terraformOutput = document.getElementById('statusMessage').textContent;
        console.log(terraformOutput); // Output the Terraform output to the console
        // Additional JavaScript code to handle the Terraform output as needed
    });
});


document.querySelectorAll('.destroyBtn').forEach(button => {
    button.addEventListener('click', async function() {
        try {
            const instanceId = this.dataset.instanceid;
            const deploymentType = this.dataset.deploymenttype;
            // console.log('Instance ID:', instanceId); // Check if instanceId is correctly extracted
            alert(instanceId);
            alert(deploymentType);
            // const row = this.closest('tr'); //Get closest table row
            // Displaying status message
            document.getElementById('statusMessage').textContent = `Destroying ${deploymentType} instance...`;

            // Apply visual indication to the table row
            const tableRow = this.closest('tr');
            tableRow.classList.add('destroying');

            let destroyRoute;
            if (deploymentType === 'Monolith') {
                destroyRoute = `/destroy-ec2?instance_id=${instanceId}`;
                // print('Deployment type is :', deploymentType)
            } else if (deploymentType === 'Lightsail') {
                destroyRoute = `/destroy-lightsail?instance_id=${instanceId}`;
                // print('Deployment type is :', deploymentType)
            }

            // Sending request to server to trigger destroy route
            const response = await fetch(destroyRoute);
            if (!response.ok) {
                throw new Error(`Failed to destroy ${deploymentType} instance.`);
            }
            const data = await response.text();
            alert(data);

            // Update status message upon successful destruction
            document.getElementById('statusMessage').textContent = `${deploymentType} instance is destroyed successfully.`;
            await updateDeploymentHistory();
            // Reload the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 2000); // Refresh after 2 seconds (adjust as needed)
        } catch (error) {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            console.error(`Error in destroying ${deploymentType} instance progress.`, error);
            // Update status message upon failure
            document.getElementById('statusMessage').textContent = `Failed to destroy ${deploymentType} instance.`;
        }
    });
});

