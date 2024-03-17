document.addEventListener('DOMContentLoaded', function() {
    const continentSelect = document.getElementById('continent');
    const regionSelect = document.getElementById('region');
    const form = document.getElementById('deployForm');
    const errorMessage = document.getElementById('errorMessage');

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
        .then(data => {
            showSuccessPopup(data);
            console.log('Success:', data);
            // Optional: Remove the line below if you want to keep users on the same page
            // window.location.href = data.wordpressInstallationUrl;
        })
        .catch(handleError);
    });
});

function showDeploymentProgressPopup() {
    document.getElementById('deploymentProgressPopup').style.display = 'flex';
}

function showSuccessPopup(data) {
    document.getElementById('deploymentProgressPopup').style.display = 'none';
    document.getElementById('deploymentSuccessPopup').style.display = 'flex';
    document.getElementById('successMessage').innerHTML = `Deployment successful! <a href="${data.wordpressInstallationUrl}" target="_blank">Access your site</a>.`;
}

function closeSuccessPopup() {
    document.getElementById('deploymentSuccessPopup').style.display = 'none';
}

function handleResponse(response) {
    if (!response.ok) {
        return response.json().then(error => Promise.reject(error));
    }
    return response.json();
}

function handleError(error) {
    console.error('Error:', error);
    document.getElementById('errorMessage').textContent = error.message || 'An error occurred during deployment';
    document.getElementById('deploymentProgressPopup').style.display = 'none';
}
