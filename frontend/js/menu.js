// const themeToggler =  document.querySelector(".theme-toggler");

// themeToggler.addEventListener('click', function (){
//     document.body.classList.toggle('dark-theme-variables')
//     themeToggler.querySelector('i:nth-child(1)').classList.toggle('active');
//     themeToggler.querySelector('i:nth-child(2)').classList.toggle('active');
// });
const baseUrl = 'http://127.0.0.1:5000';

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

document.addEventListener('DOMContentLoaded', async function() {
  const monolithDeploymentLink = document.getElementById('monolith-deployment');

  // document.getElementById('instanceCount').innerText = 'Calculating...'

  // Function to fetch instance count and update the UI
  function fetchLightsailInstanceCount() {
      // Show the loading spinner
    //   document.getElementById('loadingSpinner').style.display = 'inline-block';
      // fetch('/count-lightsail-instances')
      fetch('http://127.0.0.1:5000/count-lightsail-instances')
          .then(response => response.json())
          .then(data => {
              document.getElementById('lightsailInstanceCount').innerText = data.running_instances;
          })
          .catch(error => console.error('Error fetching instance count:', error))
          
          .finally(() => {
              // Hide the loading spinner regardless of the outcome
            //   document.getElementById('loadingSpinner').style.display = 'none';
          });
  }

  // Function to fetch instance count and update the UI
  function fetchMonolithInstanceCount() {
      // Show the loading spinner
    //   document.getElementById('loadingSpinnerMono').style.display = 'inline-block';
      fetch(`${baseUrl}/count-running-ec2-instances`)
          .then(response => response.json())
          .then(data => {
              document.getElementById('MonolithInstanceCount').innerText = data.running_instances;
          })
          .catch(error => console.error('Error fetching instance count:', error))
          
          .finally(() => {
              // Hide the loading spinner regardless of the outcome
            //   document.getElementById('loadingSpinner').style.display = 'none';
          });
  }

    //   alert("Just entered menu.js");
    // Call the function when the page is loaded
    fetchLightsailInstanceCount();
    fetchMonolithInstanceCount();

    // Call the function to fetch and populate instance status data
    fetchInstanceStatusData();
  
  
    document.addEventListener('DOMContentLoaded', function() {
      const terraformOutput = document.getElementById('statusMessage').textContent;
      console.log(terraformOutput); // Output the Terraform output to the console
      // Additional JavaScript code to handle the Terraform output as needed
    });

});

// Function to fetch instance status data from app.py
function fetchInstanceStatusData() {
    fetch('http://127.0.0.1:5000/fetch-instance-status')
    .then(response => response.json())
    .then(data => {
        // Update the status message if needed
        document.getElementById('statusMessage').textContent = 'Instance status data fetched successfully';

        // Populate the table with the received data
        const tableBody = document.getElementById('instanceStatusBody');
        tableBody.innerHTML = '';  // Clear previous content
        data.forEach(instance => {
            const row = `
                <tr>
                    <td class="px-4 py-2">${instance.deployment_id}</td>
                    <td class="px-4 py-2">${instance.creation_time}</td>
                    <td class="px-4 py-2">${instance.deployment_type}</td>
                    <td class="px-4 py-2">${instance.instance_id === "N/A" ? instance.project_id : instance.instance_id}</td>
                    <td class="px-4 py-2">${instance.blueprint_id === "N/A" ? "Wordpress" : instance.blueprint_id}</td>
                    <td class="px-4 py-2">${instance.bundle_id === "N/A" ? instance.instance_type : instance.bundle_id}</td>
                    <td class="px-4 py-2">${instance.instance_region === "N/A" ? instance.availability_zone : instance.instance_region}</td>
                    <td class="px-4 py-2">${instance.instance_state === "N/A" ? "running" : instance.instance_state}</td>
                    <td class="px-4 py-2">${instance.public_ip}</td>
                    <td class="px-4 py-2">
                        <button class="destroy-button hover:bg-red-600 text-white" data-instanceid="${instance.instance_id}" data-deploymenttype="${instance.deployment_type}" data-deploymentid="${instance.deployment_id}">Destroy</button>
                    </td>
                </tr>`;
            tableBody.innerHTML += row;
        });
    })
    .catch(error => console.error('Error:', error));
}

// Add event listener for click events on the document body
document.body.addEventListener('click', async function(event) {
    // Check if the clicked element is a "Destroy" button
    if (event.target.classList.contains('destroy-button')) {
        // Handle the click event for the "Destroy" button
        const instanceId = event.target.getAttribute('data-instanceid');
        const deploymentType = event.target.getAttribute('data-deploymenttype');
        const deploymentId = event.target.getAttribute('data-deploymentid');
        // document.getElementById('statusMessage').textContent = ``;
        
        // For testing purposes, log the instanceId and deploymentType to the console
        console.log('Instance ID:', instanceId);
        console.log('Deployment Type:', deploymentType);
        try {
            // const instanceId = this.dataset.instanceid;
            // const deploymentType = this.dataset.deploymenttype;
            // // console.log('Instance ID:', instanceId); // Check if instanceId is correctly extracted
            alert(instanceId);
            alert(deploymentType);
            alert(deploymentId);
            // const row = this.closest('tr'); //Get closest table row
            // Displaying status message
            document.getElementById('statusMessage').textContent = `Destroying ${deploymentType} instance...`;

            // Apply visual indication to the table row
            // const tableRow = this.closest('tr');
            // tableRow.classList.add('destroying');

            let destroyRoute;
            if (deploymentType === 'Monolith') {
                // alert("in the if Monolith");
                destroyRoute = `${baseUrl}/monolith/destroy-ec2?instance_id=${instanceId}&&deployment_id=${deploymentId}`;
                // print('Deployment type is :', deploymentType)
            } else if (deploymentType === 'Lightsail') {
                destroyRoute = `${baseUrl}/destroy-lightsail?instance_id=${instanceId}&&deployment_id=${deploymentId}`;
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
            // await updateDeploymentHistory();
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
    }
});


