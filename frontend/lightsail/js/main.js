document.addEventListener('DOMContentLoaded', function() {
    // Deployment page specific elements and logic
    const continentSelect = document.getElementById('continent');
    const regionSelect = document.getElementById('region');
    const form = document.getElementById('deployForm');
    const errorMessage = document.getElementById('errorMessage');

    if (continentSelect && regionSelect && form && errorMessage) {
        const regionsByContinent = {
            'Asia': [
                { id: 'ap-southeast-1', name: 'Asia Pacific (Singapore)' },
                { id: 'ap-southeast-2', name: 'Asia Pacific (Sydney)' },
                { id: 'ap-northeast-1', name: 'Asia Pacific (Tokyo)' }
            ],
            'US': [
                { id: 'us-east-1', name: 'US East (N. Virginia)' },
                { id: 'us-west-1', name: 'US West (N. California)' },
                { id: 'us-west-2', name: 'US West (Oregon)' }
            ],
            'Europe': [
                { id: 'eu-central-1', name: 'Europe (Frankfurt)' },
                { id: 'eu-west-1', name: 'Europe (Ireland)' },
                { id: 'eu-west-2', name: 'Europe (London)' },
                { id: 'eu-west-3', name: 'Europe (Paris)' },
                { id: 'eu-north-1', name: 'Europe (Stockholm)' }
            ]
        };

        continentSelect.addEventListener('change', function() {
            const regions = regionsByContinent[this.value] || [];
            regionSelect.innerHTML = ''; // Clear existing options
            regions.forEach(region => {
                let option = new Option(region.name, region.id);
                regionSelect.appendChild(option);
            });
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            showDeploymentProgressPopup();
            errorMessage.textContent = ''; // Clear any existing error messages

            const data = {
                continent: form.continent.value,
                region: form.region.value,
                blueprint: form.blueprint.value,
                sshKey: form.sshKey.value,
                instanceSize: form.instanceSize.value,
            };

            fetch('http://127.0.0.1:5000/deploy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                mode: 'cors',
            })
            .then(handleResponse)
            .then(showSuccessPopup)
            .catch(handleError);
        });
    }

    // Call fetchDeploymentHistory if on the menu.html page
    if (window.location.pathname.endsWith('menu.html')) {
        fetchDeploymentHistory();
    }
});

function showDeploymentProgressPopup() {
    const popup = document.getElementById('deploymentProgressPopup');
    if (popup) {
        popup.style.display = 'flex';
    }
}

function showSuccessPopup(data) {
    const successPopup = document.getElementById('deploymentSuccessPopup');
    const successMessage = document.getElementById('successMessage');
    if (successPopup && successMessage) {
        successMessage.innerHTML = `Deployment successful! <a href="${data.wordpressInstallationUrl}" target="_blank">Access your site</a>.`;
        successPopup.style.display = 'flex';
    }
}

function closeSuccessPopup() {
    const successPopup = document.getElementById('deploymentSuccessPopup');
    if (successPopup) {
        successPopup.style.display = 'none';
        window.location.href = 'menu.html';
    }
}

function handleResponse(response) {
    if (!response.ok) {
        return response.json().then(error => Promise.reject(error));
    }
    return response.json();
}

function handleError(error) {
    console.error('Error:', error);
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = error.message || 'An error occurred during deployment';
    }
    const progressPopup = document.getElementById('deploymentProgressPopup');
    if (progressPopup) {
        progressPopup.style.display = 'none';
    }
}


function fetchDeploymentHistory() {
    fetch('http://127.0.0.1:5000/fetch-deployment-history')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('deploymentHistoryTable');
        tableBody.innerHTML = '';  // Clear previous content
        data.forEach((deployment, index) => {
            const row = `<tr>
                            <td>${index + 1}</td>
                            <td>Lightsail</td>
                            <td>${deployment.timestamp}</td>
                            <td>${deployment.status}</td>
                         </tr>`;
            tableBody.innerHTML += row;
        });
    })
    .catch(error => console.error('Error:', error));
}








// // Function to simulate fetching a deployment status
// function fetchStatus(filename) {
//     // Simulate fetching status dynamically
//     return new Promise((resolve, reject) => {
//         // Logic to determine status, replace this with your actual implementation
//         const status = Math.random() < 0.5 ? 'Failed' : 'Succeed';
//         resolve(status);
//     });
// }

// // Function to fetch deployment history and populate a table with it
// function fetchDeploymentHistory() {
//     fetch('http://127.0.0.1:5000/fetch-deployment-history')
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(data => {
//         const tableBody = document.getElementById('deploymentHistoryTable');
//         if (!tableBody) {
//             console.error('Unable to find deploymentHistoryTable element');
//             return;
//         }
        
//         tableBody.innerHTML = '';
//         data.forEach((filename, index) => {
//             const datetime = filename.replace('XMOPSTeamTwo-', '').split('.json')[0];
//             fetchStatus(filename).then(status => {
//                 const row = `<tr>
//                                 <td>${index + 1}</td>
//                                 <td>Lightsail</td>
//                                 <td>${datetime}</td>
//                                 <td>${status}</td>
//                              </tr>`;
//                 tableBody.innerHTML += row;
//             }).catch(error => {
//                 console.error('Error fetching status:', error);
//             });
//         });
//     })
//     .catch(error => {
//         console.error('Failed to fetch deployment history:', error);
//     });
// }





























