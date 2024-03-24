document.addEventListener('DOMContentLoaded', function() {
    // Function to handle the click event for creating EC2 instance
    document.getElementById('wordpressEc2Btn').addEventListener('click', function() {
        // Displaying status message
        document.getElementById('statusMessage').textContent = 'Creating EC2 instance...';

        // Sending request to server to trigger create-ec2 route
        fetch('/worpress-install-ec2')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to create EC2 instance');
                }
                return response.text();
            })
            .then(data => {
                console.log(data); // Log the response from the server
                // Update status message upon successful creation
                document.getElementById('statusMessage').textContent = 'EC2 instance created successfully';
            })
            .catch(error => {
                console.error('Error:', error);
                // Update status message upon failure
                document.getElementById('statusMessage').textContent = 'Failed to create EC2 instance';
            });
    });

    // Function to handle the click event for creating Lightsail instance
    document.getElementById('wordpressLightsailBtn').addEventListener('click', function() {
        // Displaying status message
        document.getElementById('statusMessage').textContent = 'Creating Lightsail instance...';

        // Sending request to server to trigger create-lightsail route
        fetch('/wordpress-install-lightsail')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to create Lightsail instance');
                }
                return response.text();
            })
            .then(data => {
                console.log('Logging data from install wordpress on Lightsail in client.js', data);
                // Handle the response, e.g., display a message
                document.getElementById('statusMessage').textContent = 'Lightsail instance created successfully';
            })
            .catch(error => {
                console.error('Error:', error);
                // Update status message upon failure
                document.getElementById('statusMessage').textContent = 'Failed to create Lightsail instance';
            });
    });

    // Function to handle the click event for destroying EC2 instance
    document.getElementById('destroyEc2Btn').addEventListener('click', function() {
        // Displaying status message
        document.getElementById('statusMessage').textContent = 'Destroying EC2 instance...';

        // Sending request to server to trigger destroy-ec2 route
        fetch('/destroy-ec2')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to destroy EC2 instance');
                }
                return response.text();
            })
            .then(data => {
                console.log(data); // Log the response from the server
                // Update status message upon successful destruction
                document.getElementById('statusMessage').textContent = 'EC2 instance destroyed successfully';
            })
            .catch(error => {
                console.error('Error:', error);
                // Update status message upon failure
                document.getElementById('statusMessage').textContent = 'Failed to destroy EC2 instance';
            });
    });

    // Function to handle the click event for destroying Lightsail instance
    document.getElementById('destroyLightsailBtn').addEventListener('click', function() {
        // Displaying status message
        document.getElementById('statusMessage').textContent = 'Destroying Lightsail instance...';

        // Sending request to server to trigger destroy-lightsail route
        fetch('/destroy-lightsail')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to destroy Lightsail instance');
                }
                return response.text();
            })
            .then(data => {
                console.log(data); // Log the response from the server
                // Update status message upon successful destruction
                document.getElementById('statusMessage').textContent = 'Lightsail instance destroyed successfully';
            })
            .catch(error => {
                console.error('Error:', error);
                // Update status message upon failure
                document.getElementById('statusMessage').textContent = 'Failed to destroy Lightsail instance';
            });
    });

    //  // Fetch instance data from the server
    //  fetch('/get-instance-data')
    //  .then(response => response.json())
    //  .then(data => {
    //      // Iterate over the instance data and dynamically populate the table rows
    //      const tbody = document.getElementById('instanceStatusBody');
    //      data.forEach(instance => {
    //          const tr = document.createElement('tr');
    //          tr.innerHTML = `
    //              <td>${instance.ami_id}</td>
    //              <td>${instance.availability_zone}</td>
    //              <td>${instance.instance_id}</td>
    //              <td>${instance.instance_region}</td>
    //              <td>${instance.instance_state}</td>
    //              <td>${instance.instance_type}</td>
    //              <td>${instance.key_name}</td>
    //              <td>${instance.public_ip}</td>
    //          `;
    //          tbody.appendChild(tr);
    //      });
    //  })
    //  .catch(error => console.error('Error fetching instance data:', error));

});
