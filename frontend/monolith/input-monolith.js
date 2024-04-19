const form = document.getElementById('monolith-deployment-form');
const osDropdown = document.getElementById('aws-os');
const amiDropdown = document.getElementById('aws-ami');
const instanceTypeDropdown = document.getElementById('instance-type');
// const keyPairInput = document.getElementById('key-pair');
const existingKeyPairRadio = document.getElementById('use-existing-radio');
const newKeyPairRadio = document.getElementById('generate-new');
const existingKeyPairDropdownSelected = document.getElementById('existing-key-pair');
const existingKeyPairDropdown = document.getElementById('existing-key-pair-section');
const newKeyPairInput = document.getElementById('new-key-pair-section');
const generateKeyPairBtn = document.getElementById('generate-keypair-btn');
const newKeyPairName = document.getElementById('new-key-pair-name');

const existingSecurityGroupRadio = document.getElementById('use-existing-sg-radio');
const newSecurityGroupRadio = document.getElementById('generate-new-sg-radio');
const existingSecurityGroupDropdownSelected = document.getElementById('existing-sg');
const existingSecurityGroupDropdown = document.getElementById('existing-sg-section');
const newSecurityGroupSection = document.getElementById('new-sg-section');
const newSecurityGroupNameInput = document.getElementById('new-sg-name');
const newSecurityGroupDescriptionInput = document.getElementById('new-sg-description');
const createSecurityGroupBtn = document.getElementById('generate-sg-btn');

const allowSSHCheckbox = document.getElementById('allow-ssh');
const allowHTTPCheckbox = document.getElementById('allow-http');
const storageInput = document.getElementById('ebs-storage');
const dbTypeDropdown = document.getElementById('database_type');
const phpVersionDropdown = document.getElementById('php-version');
const webServerDropdown = document.getElementById('web-server');
// const baseUrl = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', async function() {
    const regionDropdown = document.getElementById('aws-region');

    let selectedKeyPairValue;
    let selectedSGValue;
    let newSecurityGroupDescription;
    let selectedSecurityGroupId;
    let createdSecurityGroup;
    let newSecurityGroupName;
    
    
    // Disable all input fields except the AWS Region dropdown initially
    disableInputsExceptRegion();

    // Fetch region
    const awsRegion = await fetchAWSRegions();
    
    // Populate dropdown with regions
    populateRegionDropdown(regionDropdown, awsRegion, 'Select a Region');

    // Attach event listener to region dropdown for the change events
    regionDropdown.addEventListener('change', async function(){
        const selectedRegion = regionDropdown.value;

        // Reset dependent dropdowns
        // resetDropdown(osDropdown);
        osDropdown.selectedIndex = 0;
        resetDropdown(amiDropdown);
        resetDropdown(instanceTypeDropdown);
        resetDropdown(existingKeyPairDropdownSelected);
        resetDropdown(existingSecurityGroupDropdownSelected);

        if(selectedRegion){
            // Enable the OS dropdown
            osDropdown.disabled = false;
        }
    });

    // Attach event listener to OS dropdown for the change event
    osDropdown.addEventListener('change', async function(){
        const selectedRegion = regionDropdown.value;
        const selectedOs = osDropdown.value;
        // Reset dependent dropdowns
        resetDropdown(amiDropdown);
        resetDropdown(instanceTypeDropdown);
        resetDropdown(existingKeyPairDropdownSelected);
        resetDropdown(existingSecurityGroupDropdownSelected);

        if(selectedOs){
            // Fetch AMIs based on the selected region and OS
            const amis = await fetchAMIs(selectedRegion, selectedOs);

            
            // Populate AMI dropdown with fetched AMIs
            populateAmiDropdown(amiDropdown, amis, 'Select an AMI');
            
            // // Enable the AMI dropdown
            amiDropdown.disabled = false;
        }
    });    
            
    // Attach event listener to AMI dropdown for the change event
    amiDropdown.addEventListener('change', async function(){
        const selectedRegion = regionDropdown.value;
        const selectedOs = osDropdown.value;
        const selectedAmi = amiDropdown.value;
        // Reset dependent dropdowns
        resetDropdown(instanceTypeDropdown);
        resetDropdown(existingKeyPairDropdownSelected);
        resetDropdown(existingSecurityGroupDropdownSelected);

        if (selectedAmi) {
            // Fetch instance types based on the selected region and OS
            const instanceTypes = await fetchInstanceTypes(selectedRegion, selectedOs);

            // Populate instance type dropdown with fetched instance types
            populateInstanceTypeDropdown(instanceTypeDropdown, instanceTypes, 'Select an Instance Type');
            
            // Enable the Images OS dropdown
            instanceTypeDropdown.disabled = false;
            storageInput.disabled = false;
            existingKeyPairDropdownSelected.disabled = false;

            existingKeyPairRadio.disabled = false;
            newKeyPairRadio.disabled = false;
        }
    });
                
    // Add event listeners to the radio buttons
    existingKeyPairRadio.addEventListener('change', async function() {
        
        const selectedRegion = regionDropdown.value;
        // newKeyPairRadio.style.display = 'none'
        if (existingKeyPairRadio.checked) {
            existingKeyPairDropdown.style.display = 'block';
            
            const existingKeyPairs = await fetchExistingKeyPairs(selectedRegion);
            populateExistingKeyPairDropdown(existingKeyPairs, 'Select an existing key Pair');
            newKeyPairInput.style.display = 'none';
            newSecurityGroupDescriptionInput.style.display = 'none';
            generateKeyPairBtn.style.display = 'none'; // Hide the generate button when "Use Existing Key Pair" is selected
            
            // Set the value of existingKeyPairDropdown to the first option
            if (existingKeyPairs.length > 0) {
                existingKeyPairDropdown.value = existingKeyPairs[0];
            }
        }
    });

    newKeyPairRadio.addEventListener('change', function() {
       
        // existingKeyPairRadio.style.display = 'none'
        if (newKeyPairRadio.checked) {
            existingKeyPairDropdown.style.display = 'none';
            newKeyPairInput.style.display = 'block';
            newSecurityGroupDescriptionInput.style.display = 'block';
            generateKeyPairBtn.style.display = 'block'; // Show the generate button when "Generate New Key Pair" is selected
        }
    });

    generateKeyPairBtn.addEventListener('click', async function() {
        const selectedRegion = regionDropdown.value;
        try {
            // Get the value of the new key pair name input
            const newKeyPairNameTrimmed = newKeyPairName.value.trim();
            // alert(newKeyPairName);
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
            populateExistingKeyPairDropdown(existingKeyPairs, 'Select a Key Pair');
            newKeyPairInput.style.display = 'none';
        } catch (error) {
            console.error('Error generating new key pair:', error);
            // Handle error if key pair generation fails
        }
    });

    existingKeyPairDropdown.addEventListener('change', function() {
        selectedKeyPairValue = existingKeyPairDropdownSelected.value;
        console.log('Selected key pair value:', selectedKeyPairValue); // Add this line for debugging
        existingSecurityGroupRadio.disabled = false;
        newSecurityGroupRadio.disabled = false;
        existingSecurityGroupDropdownSelected.disabled = false;
        existingSecurityGroupDropdown.disabled = false;
        allowSSHCheckbox.disabled = false;
        allowHTTPCheckbox.disabled = false;
    });

    existingSecurityGroupRadio.addEventListener('change', async function(){
        const selectedRegion = regionDropdown.value;
        if(existingSecurityGroupRadio.checked){
            existingSecurityGroupDropdown.style.display = 'block';
            newSecurityGroupSection.style.display = 'none';
            createSecurityGroupBtn.style.display = 'none';
            
            const existingSecurityGroups = await fetchExistingSecurityGroups(selectedRegion);
            console.log('Existing Security Groups', existingSecurityGroups);
            // alert(existingSecurityGroups);
            populateExistingSecurityGroupDropdown(existingSecurityGroups, 'Select a Security Group');

            // Set the value of existingSecurityGroupDropdown to the first option
            if(existingSecurityGroups.length > 0){
                existingSecurityGroupDropdown.value = existingSecurityGroups[0].id;
            }
        }
    });

    newSecurityGroupRadio.addEventListener('change', function(){
        if(newSecurityGroupRadio.checked) {
            existingSecurityGroupDropdown.style.display = 'none';
            newSecurityGroupSection.style.display = 'block';
            createSecurityGroupBtn.style.display = 'block';
            newSecurityGroupDescriptionInput.style.display = 'block'
        }
    });

    createSecurityGroupBtn.addEventListener('click', async function() {
        try{
            // Get the value of the new security group name 
            newSecurityGroupName = newSecurityGroupNameInput.value.trim();
            newSecurityGroupDescription = newSecurityGroupDescriptionInput.value.trim();
            console.log('newSecurityGroupName :', newSecurityGroupName);
            console.log('newSecurityGroupDescription :', newSecurityGroupDescription);
            // alert(newSecurityGroupName);
            // alert(newSecurityGroupDescription);
            if(!newSecurityGroupName || !newSecurityGroupDescription){
                alert('Please enter a name for the new security group');
                return;
            }
            newSecurityGroupSection.style.display = 'block';
            // Create a new paragraph element to display the name and description
            const paragraph = document.createElement('p');
            paragraph.textContent = `Name: ${newSecurityGroupName}, Description: ${newSecurityGroupDescription}`;
            // Apply styles to the paragraph
            paragraph.style.color = 'green';
            // Get the container element to append the paragraph
            const newSGSection = document.getElementById('new-sg-section');
            newSGSection.appendChild(paragraph);
            const selectedRegion = regionDropdown.value;
            newSecurityGroupNameInput.style.display = 'none';
            newSecurityGroupDescriptionInput.style.display = 'none';
            createSecurityGroupBtn.style.display = 'none';
            // newSecurityGroupSection.style.display = 'none';
            // existingSecurityGroupDropdown.style.display = 'none';
        } catch (error){
            console.error('Error creating new security group:', error);
            // Handle error if creation fails
        }
    });

    existingSecurityGroupDropdown.addEventListener('change', async function(){
        // Accessing the selected option directly and retrieving its value object
        const selectedOptionValue = document.getElementById('existing-sg').value;
        // Splitting the value string using colon as the delimiter
        const parts = selectedOptionValue.split(':');
        if(parts.length >= 2){
            // Accessing the GroupName and GroupId properties
            selectedSGValue = parts[0].trim();
            selectedSecurityGroupId = parts[1].trim();

            // selectedSGValue = existingSecurityGroupDropdownSelected.value;
            console.log('Selected SG value NO JSONIFY:', selectedSGValue);
            // console.log('Selected SG value NO JSONIFY:', selectedSecurityGroupId);
            // console.log('Selected SG value:', JSON.stringify(selectedSGValue), null, 2);
            console.log('Selected SG ID: ', selectedSecurityGroupId );
        } else {
            console.error('Invalid format for selected option value:', selectedOptionValue);
        }
        

    });

    storageInput.addEventListener('change', function(){
        dbTypeDropdown.disabled = false;
    });

    dbTypeDropdown.addEventListener('change', function(){
        // alert('Hey');
        phpVersionDropdown.disabled = false;
    });
    phpVersionDropdown.addEventListener('change', function(){
        // alert('Hey');
        webServerDropdown.disabled = false;
    });

                            
    // Add event listener for form submission
    form.addEventListener('submit', async function(event) {
        // console.log("id here", uniqueInstance);
        try {
             // Prevent the default form submission behavior
            event.preventDefault();
            showDeploymentProgressPopup();

            // Gather the form data
            const formData = new FormData(form);
            // Include the selected key pair value in the form data
            formData.append('key_pair', selectedKeyPairValue);
            formData.append('security_group', selectedSGValue);
            formData.append('security_group_description', newSecurityGroupDescription);
            formData.append('selectedSGId', selectedSecurityGroupId);
            formData.append('createdSG', createdSecurityGroup)
            formData.append('newSecurityGroupName', newSecurityGroupName)

            // Convert FormData to JSON object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            // alert(JSON.stringify(data));
            const message = 'EC2 instance is being created.....'
            alert(data);
           
            // Redirect to the main page
            // window.location.href = 'http://127.0.0.1:8000/menu.html';
          
            // Send the form data to the server
            const response = await fetch(`${baseUrl}/monolith/deploy-monolith`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(handleResponse)
            .then(showSuccessPopup)
            .catch(handleError);
            // Reload the page after a short delay
            // window.location.href = '/';
            // setTimeout(() => {
            //     window.location.reload();
            // }, 1000); // Refresh after 1 seconds (adjust as needed)
        } catch (error){
            console.error('Error on submitting forms for Monolith deployment ', error);
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
            window.location.href = '../../menu.html';
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

    // Function to fetch AWS regions
    async function fetchAWSRegions() {
        let elapsedTime;
        let timerInterval; // Variable to store the timer interval ID
        try {

            // Show generating message
            const messageElement = document.getElementById('region-generation-message');
            messageElement.textContent = `Generating potential operating systems for region ...`;

            // // Apply green color
            messageElement.style.color = '#008000'; // This is the hexadecimal value for green color
            messageElement.style.fontSize = '8px'; // Font size 14px

            // Start time
            const startTime = Date.now();

            // Update message with elapsed time every second
            timerInterval = setInterval(() => {
                const elapsedTime = Math.floor((Date.now() - startTime) / 1000); // Calculate elapsed time in seconds
                messageElement.textContent = `Generating potential operating systems for region ... (Elapsed time: ${elapsedTime} seconds)`;
            }, 1000); // Update every second

            // Check if AWS regions are already stored in session storage
            const storedRegions = sessionStorage.getItem('aws_regions');
            if(storedRegions){
                clearInterval(timerInterval);
                const endTime = Date.now();
                elapsedTime = Math.floor((endTime-startTime) / 1000);
                messageElement.textContent = `(Elapsed time: ${elapsedTime} seconds to fetch all OS )`;

                return JSON.parse(storedRegions);
            }
            
            // const response = await fetch('/monolith/get-regions');
            const response = await fetch(`${baseUrl}/monolith/get-regions`);
            const data = await response.json();
            console.log(`Consoling data, ${data}`);

            // Store AWS regions in session storage
            sessionStorage.setItem('aws_regions', JSON.stringify(data.regions));

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
            // alert('I am in fetchAMIs');
            const response = await fetch(`${baseUrl}/monolith/amis?region=${region}&os_type=${osType}`);
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
            const response = await fetch(`${baseUrl}/monolith/instance-types?region=${region}&os_type=${osType}`);
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
            const response = await fetch(`${baseUrl}/monolith/existing_key_pairs?region=${region}`);
            const data = await response.json();
            // alert(data);
            return data.existing_key_pairs;
        } catch (error) {
            console.error('Error fetching existing key pairs: ', error);
        }
    }

    // Function to Post new 
    async function generateKeyPair(newKeyPairName, selectedRegion) {
        try {
            const response = await fetch(`${baseUrl}/monolith/generate_key_pair`, {
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

    async function createSecurityGroup (sg_name, sg_description, selectedRegion){
        try{
            const response = await fetch(`${baseUrl}/monolith/create_security_group`, {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    region: selectedRegion,
                    new_sg_name: sg_name,
                    new_sg_description: sg_description
                })
            });
            const data = await response.json();
            return data.generated_sg;
        } catch (error){
            console.error('Error Creating new SG :', error);
        }
    }

    async function fetchExistingSecurityGroups(selectedRegion){
        try{
            const response = await fetch(`${baseUrl}/monolith/get-security-groups?region=${selectedRegion}`);
            const data = await response.json();
            console.log('Existing SGs from Fetched',data.security_groups);
            return data.security_groups;
        } catch (error){
            throw new Error('Error retreiving existing security groups');
        }
    }
    
});

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
        // Check if there's an existing paragraph displaying the count
        const existingAmiCountParagraph = dropdown.parentNode.querySelector('.ami-count-paragraph');
        if(existingAmiCountParagraph){
            existingAmiCountParagraph.remove();
        }
        // // Display the total count in a paragraph element
        const amiCountParagraph = document.createElement('p');
        amiCountParagraph.textContent = `Total available AMIs: ${amiCount}`;
        amiCountParagraph.style.color = 'blue'; // Set color to blue
        amiCountParagraph.style.fontSize = '8px'; // Set font size to smaller
        amiCountParagraph.classList.add('ami-count-paragraph'); // Add a class for easy identification
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
        // Check if there's an existing paragraph displaying the count
        const existingTypeCountParagraph = dropdown.parentNode.querySelector('.instype-count-paragraph');
        if(existingTypeCountParagraph){
            existingTypeCountParagraph.remove();
        }
        // Display the total count in a paragraph element
        const instanceTypeCountParagraph = document.createElement('p');
        instanceTypeCountParagraph.textContent = `Total available InstanceTypes: ${instanceTypeCount}`;
        instanceTypeCountParagraph.style.color = 'blue'; // Set color to blue
        instanceTypeCountParagraph.style.fontSize = '8px'; // Set font size to smaller
        instanceTypeCountParagraph.classList.add('instype-count-paragraph');
        dropdown.parentNode.insertBefore(instanceTypeCountParagraph, dropdown.nextSibling);

        instanceTypes.forEach(type => {
            const optionElement = document.createElement('option');
            optionElement.value = type;
            optionElement.textContent = `${type}:  `;
            dropdown.appendChild(optionElement);
        });
    }

    // Function to populate existing key pair dropdown with options
    function populateExistingKeyPairDropdown(existingKeyPairs, placeholder) {
        const dropdown = document.getElementById('existing-key-pair');
        dropdown.innerHTML = '';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = 'Select a key pair';
        placeholderOption.textContent = placeholder;
        dropdown.appendChild(placeholderOption)
        existingKeyPairs.forEach(keyPair => {
            const optionElement = document.createElement('option');
            optionElement.value = keyPair;
            optionElement.textContent = keyPair;
            dropdown.appendChild(optionElement);
        });
    }

    // Function to populate existing security groups dropdown with options
    function populateExistingSecurityGroupDropdown(existingSecurityGroups, placeholder){
        const dropdown = document.getElementById('existing-sg');
        dropdown.innerHTML = '';

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        dropdown.appendChild(placeholderOption)

        console.log('Existing Security groups in PopulateExistingSG ', existingSecurityGroups);
        existingSecurityGroups.forEach(sg =>{
            const optionElement = document.createElement('option');
            // optionElement.value = sg.GroupName;
            optionElement.value = `${sg.GroupName}:${sg.GroupId}`;;
            console.log('Selected Element value', optionElement);
            const selectedSecurityGroupId = sg.GroupId;
            console.log('Selected SG ID in Population function',selectedSecurityGroupId );
            optionElement.textContent = `${sg.GroupName}: ${sg.GroupId}`;
            // optionElement.textContent = sg;
            dropdown.appendChild(optionElement);
        });
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
        // keyPairInput.disabled = true;
        existingKeyPairRadio.disabled = true;
        newKeyPairRadio.disabled = true;
        existingSecurityGroupRadio.disabled = true;
        newSecurityGroupRadio.disabled = true;
        allowSSHCheckbox.disabled = true;
        allowHTTPCheckbox.disabled = true;
        storageInput.disabled = true;
        dbTypeDropdown.disabled = true;
        phpVersionDropdown.disabled = true;
        webServerDropdown.disabled = true;
        // submitButton.disabled = true;

    }
// });

// Function to reset a dropdown to its initial state
function resetDropdown(dropdown) {
    dropdown.innerHTML = '';
    dropdown.disabled = true;
}

 