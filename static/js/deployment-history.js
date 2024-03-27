document.addEventListener('DOMContentLoaded', async function() {
    // alert('Deployment history page is loaded');
    let deploymentHistory; // Declare deploymentHistory variable

    try{
        const response = await fetch('/get-deployment-history');
        if(!response.ok){
            throw new Error('Failed to fetch deployment history');
        }

        const deploymentHistory = await response.json();
        console.log('Deployment history: ', deploymentHistory);

        populateTable(deploymentHistory);
    } catch (error) {
        console.error('Error fetching deployment history:', error);
    }

    // Add event listeners to the buttons
    document.getElementById('backButton').addEventListener('click', function() {
        // Go back to the previous page
        window.history.back();
    });

    document.getElementById('downloadButton').addEventListener('click', async function() {
        // Placeholder functionality for download button
        // alert('Downloading deployment history...');
        // alert (typeof deploymentHistory);
        // alert(JSON.stringify(deploymentHistory));
        // // Implement actual download functionality here
        // if(!deploymentHistory){
        //     console.error('Deployment history not available.');
        //     return;
        // }

        // // Convert deployment History to CSV format
        // const csvData = convertToCSV(deploymentHistory);
        // // Trigger download 
        // downloadCSV(csvData, 'deployment-history.csv');

        try{
            // Fetch history Json data from the server
            const response = await fetch('/get-deployment-history');
            alert (response);
            console.log('Deployment history: ', response);
           
            if(!response){
                console.error('Deployment history not available.');
                return;
            }
            // Parse JSON data from the response body
            const deploymentHistory = await response.json();
            console.log('Extracted data from response', deploymentHistory)
             // Convert deployment History to CSV format
            const csvData = convertToCSV(deploymentHistory);
            // Trigger download 
            downloadCSV(csvData, 'deployment-history.csv');
        } catch (error) {
            console.error('Error fetching all history data:', error);
        }


    });

    document.getElementById('sendEmailButton').addEventListener('click', function() {
        // Placeholder functionality for send email button
        alert('Sending email with deployment history...');
        // Implement actual send email functionality here
    });
    
});

function populateTable(deploymentHistory){
    const tableBody = document.getElementById('historyTableBody');
    deploymentHistory.forEach(entry => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${entry.deployment_type}</td>
            <td>${entry.creation_time}</td>
            <td>${entry.deletion_time}</td>
            <td>${entry.availability_zone}</td>
            <td>${entry.instance_id !== 'N/A' ? entry.instance_id : entry.ami_id}</td>
            <td>${entry.instance_region !== 'N/A' ? entry.instance_region : entry.availability_zone}</td>
            <td>${entry.instance_type !== 'N/A' ? entry.instance_type: entry.bundle_id}</td>
            <td>${entry.project_id}</td>
            <td>${entry.instance_state}</td>
        `;
        tableBody.appendChild(row);
    })
}

function convertToCSV(data){
    const csvRows = [];
    // Header row
    csvRows.push(Object.keys(data[0]).join(','));
    // Data row
    data.forEach(row => {
        const values = Object.values(row).map(value => `"${value}"`);
        csvRows.push(values.join(','));
    });
    return csvRows.join('\n')
}

function downloadCSV(csvData, fileName){
    const blob = new Blob([csvData], {type: 'text/csv'});
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
 