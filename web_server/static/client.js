document.addEventListener('DOMContentLoaded', async function() {
    const wordpressEc2Btn = document.getElementById('wordpressEc2Btn');
    if (wordpressEc2Btn) {
        wordpressEc2Btn.addEventListener('click', () => {
            window.location.href = './static/monolith-deployment.html';
            // window.location.href = './static/lightsail-deployment.html';
        });
    } else {
        console.error("Button with ID 'wordpressEc2Btn' not found.");
    }

    const wordpressLightsailBtn = document.getElementById('wordpressLightsailBtn');
    if (wordpressLightsailBtn) {
        wordpressLightsailBtn.addEventListener('click', () => {
            window.location.href = './static/lightsail-deployment.html';
            // window.location.href = './static/lightsail-deployment.html';
        });
    } else {
        console.error("Button with ID 'wordpressEc2Btn' not found.");
    }

    document.addEventListener('DOMContentLoaded', function() {
        const terraformOutput = document.getElementById('statusMessage').textContent;
        console.log(terraformOutput); // Output the Terraform output to the console
        // Additional JavaScript code to handle the Terraform output as needed
    });
    

    // document.addEventListener('DOMContentLoaded', async function() {
    //     try {
    //         // Fetch deployment history data from S3 bucket
    //         const response = await fetch('/destroy-ec2');
    //         const historyData = await response.json();
    
    //         // Select the tbody element where the history will be populated
    //         const historyTableBody = document.getElementById('historyTableBody');
    
    //         // Iterate through the deployment history data and populate the table
    //         historyData.forEach(entry => {
    //             const row = historyTableBody.insertRow(); // Insert a new row
    //             // Add cells to the row and populate them with data
    //             row.insertCell(0).textContent = entry.timestamp;
    //             row.insertCell(1).textContent = entry.type;
    //             row.insertCell(2).textContent = entry.status;
    //         });
    //     } catch (error) {
    //         console.error('Error fetching or populating deployment history:', error);
    //     }
    // });

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

// Add event listener for the destroy Lightsail button
// document.getElementById('destroyLightsailBtn').addEventListener('click', async function() {
//     try {
//         // Displaying status message
//         document.getElementById('statusMessage').textContent = 'Destroying Lightsail instance...';

//         // Sending request to server to trigger destroy-ec2 route
//         const response = await fetch('/destroy-lightsail');
//         if (!response.ok) {
//             throw new Error('Failed to destroy Lightsail instance');
//         }
//         const data = await response.text();
//         console.log(data); // Log the response from the server
//         // Update status message upon successful destruction
//         document.getElementById('statusMessage').textContent = 'Lightsail instance destroyed successfully';
//         await updateDeploymentHistory();
//         // Reload the page after a short delay
//         setTimeout(() => {
//             window.location.reload();
//         }, 2000); // Refresh after 1 seconds (adjust as needed)

//         // Call the function to update deployment history after destroying EC2
//         // await updateDeploymentHistory();
//     } catch (error) {
//         setTimeout(() => {
//             window.location.reload();
//         }, 1000); // Refresh after 1 seconds (adjust as needed)
//         console.error('Error:', error);
//         // Update status message upon failure
//         document.getElementById('statusMessage').textContent = 'Failed to destroy Lightsail instance';
//     }
// });