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

     // Function to handle the click event for creating Lightsail instance
    //  document.getElementById('wordpressLightsailBtn').addEventListener('click', async function() {
    //     try {
    //         // Displaying status message
    //         document.getElementById('statusMessage').textContent = 'Creating Lightsail instance...';

    //         // Sending request to server to trigger create-lightsail route
    //         const response = await fetch('/wordpress-install-lightsail');
    //         if (!response.ok) {
    //             throw new Error('Failed to create Lightsail instance');
    //         }
    //         const data = await response.text();
    //         console.log('Logging data from install wordpress on Lightsail in client.js', data);
    //         // Handle the response, e.g., display a message
    //         document.getElementById('statusMessage').textContent = 'Lightsail instance created successfully';
    //         // Reload the page after a short delay
    //         setTimeout(() => {
    //             window.location.reload();
    //         }, 1000); // Refresh after 1 seconds (adjust as needed)
    //     } catch (error) {
    //         console.error('Error:', error);
    //         // Update status message upon failure
    //         document.getElementById('statusMessage').textContent = 'Failed to create Lightsail instance';
    //     }
    // });

    // Function to handle the click event for destroying EC2 instance
    // document.getElementById('destroyEc2Btn').addEventListener('click', async function() {
    //     try {
    //         // Displaying status message
    //         document.getElementById('statusMessage').textContent = 'Destroying EC2 instance...';

    //         // Sending request to server to trigger destroy-ec2 route
    //         const response = await fetch('/destroy-ec2');
    //         if (!response.ok) {
    //             throw new Error('Failed to destroy EC2 instance');
    //         }
    //         const data = await response.text();
    //         console.log(data); // Log the response from the server
    //         // Update status message upon successful destruction
    //         document.getElementById('statusMessage').textContent = 'EC2 instance destroyed successfully';
    //         // Reload the page after a short delay

    //         setTimeout(() => {
    //             window.location.reload();
    //         }, 2000); // Refresh after 1 seconds (adjust as needed)
    //     } catch (error) {
    //         console.error('Error:', error);
    //         // Update status message upon failure
    //         document.getElementById('statusMessage').textContent = 'Failed to destroy EC2 instance';
    //     }
    // });

    // Function to handle the click event for destroying Lightsail instance
    document.getElementById('destroyLightsailBtn').addEventListener('click', async function() {
        try {
            // Displaying status message
            document.getElementById('statusMessage').textContent = 'Destroying Lightsail instance...';

            // Sending request to server to trigger destroy-lightsail route
            const response = await fetch('/destroy-lightsail');
            if (!response.ok) {
                throw new Error('Failed to destroy Lightsail instance');
            }
            const data = await response.text();
            console.log(data); // Log the response from the server
            // Update status message upon successful destruction
            document.getElementById('statusMessage').textContent = 'Lightsail instance destroyed successfully';
        } catch (error) {
            console.error('Error:', error);
            // Update status message upon failure
            document.getElementById('statusMessage').textContent = 'Failed to destroy Lightsail instance';
        }
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



// document.addEventListener('DOMContentLoaded', async function() {
//     try {
//         // Function to handle the click event for creating EC2 instance
//         document.getElementById('wordpressEc2Btn').addEventListener('click', async function() {
//             try {
//                 // Displaying status message
//                 document.getElementById('statusMessage').textContent = 'Creating EC2 instance...';

//                 // Sending request to server to trigger create-ec2 route
//                 const response = await fetch('/worpress-install-ec2');
//                 if (!response.ok) {
//                     throw new Error('Failed to create EC2 instance');
//                 }
//                 const data = await response.text();
//                 console.log(data); // Log the response from the server
//                 // Update status message upon successful creation
//                 document.getElementById('statusMessage').textContent = 'EC2 instance created successfully';
//                 // Reload the page after a short delay
//                 setTimeout(() => {
//                     window.location.reload();
//                 }, 1000); // Refresh after 2 seconds (adjust as needed)
//             } catch (error) {
//                 console.error('Error:', error);
//                 // Update status message upon failure
//                 document.getElementById('statusMessage').textContent = 'Failed to create EC2 instance';
//             }
//         });

       

        // Initial fetch and update of instance data when the page loads
        // await fetchAndUpdateInstanceData();
//     } catch (error) {
//         console.error('Error:', error);
//     }
// });
// Define a function to fetch deployment history data and update the table
// async function updateDeploymentHistory() {
//     try {
//         // Fetch deployment history data from the server
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
// }

// Add event listener for the destroy EC2 button
document.getElementById('destroyEc2Btn').addEventListener('click', async function() {
    try {
        // Displaying status message
        document.getElementById('statusMessage').textContent = 'Destroying EC2 instance...';

        // Sending request to server to trigger destroy-ec2 route
        const response = await fetch('/destroy-ec2');
        if (!response.ok) {
            throw new Error('Failed to destroy EC2 instance');
        }
        const data = await response.text();
        console.log(data); // Log the response from the server
        // Update status message upon successful destruction
        document.getElementById('statusMessage').textContent = 'EC2 instance destroyed successfully';
        await updateDeploymentHistory();
        // Reload the page after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 2000); // Refresh after 1 seconds (adjust as needed)

        // Call the function to update deployment history after destroying EC2
        // await updateDeploymentHistory();
    } catch (error) {
        setTimeout(() => {
            window.location.reload();
        }, 1000); // Refresh after 1 seconds (adjust as needed)
        console.error('Error:', error);
        // Update status message upon failure
        document.getElementById('statusMessage').textContent = 'Failed to destroy EC2 instance';
    }
});

// Call the function to update deployment history when the page loads
// document.addEventListener('DOMContentLoaded', async function() {
//     await updateDeploymentHistory();
// });