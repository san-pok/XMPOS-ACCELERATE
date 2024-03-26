document.addEventListener('DOMContentLoaded', async function() {
    const form = document.getElementById('monolith-deployment-form');
    const regionDropdown = document.getElementById('aws-region');
    // const imageDropdown = document.getElementById('aws-os');
    // const osTypeCheckboxes = document.querySelectorAll('input[name="os-type"]');
    const osDropdown = document.getElementById('aws-os');
    const amiDropdown = document.getElementById('aws-ami');
    const instanceTypeDropdown = document.getElementById('instance-type');
    const keyPairInput = document.getElementById('key-pair');
    // const existingKeyPair = document.getElementById('use-existing');
    const existingKeyPairRadio = document.getElementById('use-existing-radio');
    const existingKeyPairDropdownSelected = document.getElementById('existing-key-pair');
    const newKeyPairRadio = document.getElementById('generate-new');
    const existingKeyPairDropdown = document.getElementById('existing-key-pair-section');
    const newKeyPairInput = document.getElementById('new-key-pair-section');
    const generateKeyPairBtn = document.getElementById('generate-keypair-btn');
    const newKeyPairName = document.getElementById('new-key-pair-name');
    const allowSSHCheckbox = document.getElementById('allow-ssh');
    const allowHTTPCheckbox = document.getElementById('allow-http');
    const storageInput = document.getElementById('ebs-storage');
    const dbTypeDropdown = document.getElementById('db-type');
    const phpVersionDropdown = document.getElementById('php-version');
    const webServerDropdown = document.getElementById('web-server');
    // const uniqueInstance = document.getElementById('unique-instance').innerHTML;
    // Define a variable to store the selected key pair value
    let selectedKeyPairValue;
    
    // Disable all input fields except the AWS Region dropdown initially
    disableInputsExceptRegion();

    // Fetch region
    const awsRegion = await fetchAWSRegions();
    
    // Populate dropdown with regions
    populateRegionDropdown(regionDropdown, awsRegion, 'Select a Region');

     // Attach event listener to region dropdown for the change events
     regionDropdown.addEventListener('change', async function(){
        const selectedRegion = regionDropdown.value;

        // Enable the OS dropdown
        osDropdown.disabled = false;

        // Attach event listener to OS dropdown for the change event
        osDropdown.addEventListener('change', async function(){
            const selectedOs = osDropdown.value;

            // Enable the AMI dropdown
            // amiDropdown.disabled = false;
            // Fetch AMIs based on the selected region and OS
            const amis = await fetchAMIs(selectedRegion, selectedOs);

            // Populate AMI dropdown with fetched AMIs
            populateAmiDropdown(amiDropdown, amis, 'Select an AMI');

            // // Enable the AMI dropdown
            amiDropdown.disabled = false;

            // Fetch instance types based on the selected region and OS
            const instanceTypes = await fetchInstanceTypes(selectedRegion, selectedOs);

            // Populate instance type dropdown with fetched instance types
            populateInstanceTypeDropdown(instanceTypeDropdown, instanceTypes, 'Select an Instance Type');
            
            // Enable the Images OS dropdown
            instanceTypeDropdown.disabled = false;
            storageInput.disabled = false;

            existingKeyPairRadio.disabled = false;
            newKeyPairRadio.disabled = false;

            // Add event listeners to the radio buttons
            existingKeyPairRadio.addEventListener('change', async function() {
                if (existingKeyPairRadio.checked) {
                    existingKeyPairDropdown.style.display = 'block';
                    const existingKeyPairs = await fetchExistingKeyPairs(selectedRegion);
                    populateExistingKeyPairDropdown(existingKeyPairs);
                    newKeyPairInput.style.display = 'none';
                    generateKeyPairBtn.style.display = 'none'; // Hide the generate button when "Use Existing Key Pair" is selected
                    
                    // Set the value of existingKeyPairDropdown to the first option
                    if (existingKeyPairs.length > 0) {
                        existingKeyPairDropdown.value = existingKeyPairs[0];
                    }
                }
            });

            newKeyPairRadio.addEventListener('change', function() {
                if (newKeyPairRadio.checked) {
                    existingKeyPairDropdown.style.display = 'none';
                    newKeyPairInput.style.display = 'block';
                    generateKeyPairBtn.style.display = 'block'; // Show the generate button when "Generate New Key Pair" is selected
                }
            });

        });
        generateKeyPairBtn.addEventListener('click', async function() {
            try {
                // Get the value of the new key pair name input
                const newKeyPairNameTrimmed = newKeyPairName.value.trim();
                if (!newKeyPairNameTrimmed) {
                    // Handle case when the input is empty
                    alert('Please enter a name for the new key pair.');
                    return;
                }

                // Call your function to generate a new key pair here, passing the new key pair name and selected region
                const generatedKeyPair = await generateKeyPair(newKeyPairNameTrimmed, selectedRegion);
                
                // Display the generated key pair in the existing key pair dropdown
                existingKeyPairDropdown.style.display = 'block';
                const existingKeyPairs = await fetchExistingKeyPairs(selectedRegion);
                existingKeyPairs.push(generatedKeyPair); // Assuming newKeyPairName is the name of the generated key pair
                populateExistingKeyPairDropdown(existingKeyPairs);
                newKeyPairInput.style.display = 'none';
            } catch (error) {
                console.error('Error generating new key pair:', error);
                // Handle error if key pair generation fails
            }
        });

        existingKeyPairDropdown.addEventListener('change', function() {
            selectedKeyPairValue = existingKeyPairDropdownSelected.value;
            console.log('Selected key pair value:', selectedKeyPairValue); // Add this line for debugging
        });
        

        
     });

    // Add event listener for form submission
    form.addEventListener('submit', async function(event) {
        // console.log("id here", uniqueInstance);
        try {
             // Prevent the default form submission behavior
            event.preventDefault();

            // Gather the form data
            const formData = new FormData(form);
            // Include the selected key pair value in the form data
            formData.append('key_pair', selectedKeyPairValue);

            // Convert FormData to JSON object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            alert(JSON.stringify(data));
            const message = 'EC2 instance is being created.....'
            alert(data);
            // updateStatusMessage(message);
            // Redirect to index.html with message as query parameter
            // window.location.href = '/index.html?message=' + encodeURIComponent(message);

            // Redirect to the main page
            window.location.href = '/';
          
            // Send the form data to the server
            
            const response = await fetch('/monolith/deploy-monolith', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            
            // Reload the page after a short delay
            // window.location.href = '/';
            setTimeout(() => {
                window.location.reload();
            }, 1000); // Refresh after 1 seconds (adjust as needed)
        // Redirect to the main page
        // window.location.href = '/';    

        } catch (error){
            console.error('Error on submitting forms for Monolith deployment ', error);
        }

    });


    // Function to fetch AWS regions
    async function fetchAWSRegions() {
        let elapsedTime;
        let timerInterval; // Variable to store the timer interval ID
        try {

            // Show generating message
            const messageElement = document.getElementById('region-generation-message');
            messageElement.textContent = `Generating potential operating systems for region ...`;

            // Apply green color
            messageElement.style.color = '#008000'; // This is the hexadecimal value for green color
            messageElement.style.fontSize = '14px'; // Font size 14px

            // Start time
            const startTime = Date.now();

            // Update message with elapsed time every second
            timerInterval = setInterval(() => {
                const elapsedTime = Math.floor((Date.now() - startTime) / 1000); // Calculate elapsed time in seconds
                messageElement.textContent = `Generating potential operating systems for region ... (Elapsed time: ${elapsedTime} seconds)`;
            }, 1000); // Update every second

            const response = await fetch('/monolith/get-regions');
            const data = await response.json();
            console.log(`Consoling data, ${data}`);

            // Clear generating message and stop the timer
            clearInterval(timerInterval);
            const endTime = Date.now();
            elapsedTime = Math.floor((endTime-startTime)/1000);
            messageElement.textContent = `(Elapsed time: ${elapsedTime} seconds to fetch all OS)`;

            return data.regions;
        } catch (error) {
            console.error('Error fetching AWS regions: ', error);
            return [];
        }
    }

    // Function to fetch AMIs based on selected region and OS
    async function fetchAMIs(region, osType) {
        try {
            alert('I am in fetchAMIs');
            const response = await fetch(`/monolith/amis?region=${region}&os_type=${osType}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching AMIs: ', error);
            return [];
        }
    }

    // Function to fetch instance types based on selected region and OS
    async function fetchInstanceTypes(region, osType) {
        try {
            const response = await fetch(`/monolith/instance-types?region=${region}&os_type=${osType}`);
            const data = await response.json();
            console.log(data.instance_types);
            return data.instance_types;
        } catch (error) {
            console.error('Error fetching instance types: ', error);
            return [];
        }
    }

    // Function to fetch existing key pairs based on selected region
    async function fetchExistingKeyPairs(region) {
        try {
            const response = await fetch(`/monolith/existing_key_pairs?region=${region}`);
            const data = await response.json();
            alert(data);
            return data.existing_key_pairs;
        } catch (error) {
            console.error('Error fetching existing key pairs: ', error);
        }
    }

    // Function to Post new 
    async function generateKeyPair(newKeyPairName, selectedRegion) {
        try {
            const response = await fetch('/monolith/generate_key_pair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    region: selectedRegion,
                    new_key_pair_name: newKeyPairName
                })
            });
            const data = await response.json();
            return data.generated_key_pair;
        } catch (error) {
            throw new Error('Error generating key pair');
        }
    }
    



    //Function to populate drop down with options
    function populateRegionDropdown(dropdown, options, placeholder){
        dropdown.innerHTML='';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        dropdown.appendChild(placeholderOption)
        // console.log(options);
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.RegionName;
            // alert(optionElement.value);
            optionElement.textContent = `${option.RegionName}: ${option.DisplayName}`;
            dropdown.appendChild(optionElement);
        });
    }

    function populateAmiDropdown(dropdown, amis, placeholder){
        
        dropdown.innerHTML='';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        dropdown.appendChild(placeholderOption)
        const amisJSON = JSON.stringify(amis, null, 2);
        // console.log(amisJSON);
        // console.log(options);

        // Count the total number of AMIs
        const amiCount = amis.length;

        // Display the total count in a paragraph element
        const amiCountParagraph = document.createElement('p');
        amiCountParagraph.textContent = `Total available AMIs: ${amiCount}`;
        amiCountParagraph.style.color = 'blue'; // Set color to blue
        amiCountParagraph.style.fontSize = '14px'; // Set font size to smaller
        dropdown.parentNode.insertBefore(amiCountParagraph, dropdown.nextSibling);
        
        amis.forEach(ami => {
            // console.log(ami);
            const optionElement = document.createElement('option');
            optionElement.value = ami.ImageId;
            optionElement.textContent = `${ami.ImageId}: ${ami.ImageType}`;
            dropdown.appendChild(optionElement);
        });
    }

    // Function to populate instance type dropdown with options
    function populateInstanceTypeDropdown(dropdown, instanceTypes, placeholder){
        dropdown.innerHTML='';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        dropdown.appendChild(placeholderOption)

        // Count the total number of AMIs
        const instanceTypeCount = instanceTypes.length;

        // Display the total count in a paragraph element
        const instanceTypeCountParagraph = document.createElement('p');
        instanceTypeCountParagraph.textContent = `Total available InstanceTypes: ${instanceTypeCount}`;
        instanceTypeCountParagraph.style.color = 'blue'; // Set color to blue
        instanceTypeCountParagraph.style.fontSize = '14px'; // Set font size to smaller
        dropdown.parentNode.insertBefore(instanceTypeCountParagraph, dropdown.nextSibling);

        instanceTypes.forEach(type => {
            const optionElement = document.createElement('option');
            optionElement.value = type;
            optionElement.textContent = `${type}:  `;
            dropdown.appendChild(optionElement);
        });
    }

    // Function to populate existing key pair dropdown with options
    function populateExistingKeyPairDropdown(existingKeyPairs) {
        const dropdown = document.getElementById('existing-key-pair');
        dropdown.innerHTML = '';
        existingKeyPairs.forEach(keyPair => {
            const optionElement = document.createElement('option');
            optionElement.value = keyPair;
            optionElement.textContent = keyPair;
            dropdown.appendChild(optionElement);
        });
    }

    // Function to generate a new key pair
    async function generateNewKeyPair(keyPairName) {
        try {
            // Send a request to your Flask backend to generate a new key pair
            const response = await fetch('/generate-key-pair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ keyPairName })
            });
            const data = await response.json();
            console.log('New key pair generated:', data);
        } catch (error) {
            console.error('Error generating new key pair:', error);
        }
    }


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

    // Function to disable all input fields except the AWS Region dropdown
    function disableInputsExceptRegion() {
        // imageDropdown.disabled = true;
        osDropdown.disabled =true;
        amiDropdown.disabled = true;
        instanceTypeDropdown.disabled = true;
        // osTypeCheckbox.disabled=true;
        keyPairInput.disabled = true;
        existingKeyPairRadio.disabled = true;
        newKeyPairRadio.disabled = true;
        allowSSHCheckbox.disabled = true;
        allowHTTPCheckbox.disabled = true;
        storageInput.disabled = true;
        dbTypeDropdown.disabled = true;
        phpVersionDropdown.disabled = true;
        webServerDropdown.disabled = true;
        // submitButton.disabled = true;

    }
});

// Function to handle the alert
function showAlert() {
    alert("Input Monolith page loaded!");
}
 