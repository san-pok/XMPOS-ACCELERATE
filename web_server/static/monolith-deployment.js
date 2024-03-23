document.addEventListener('DOMContentLoaded', async function() {
    const form = document.getElementById('monolith-deployment-form');
    const regionDropdown = document.getElementById('aws-region');
    // const imageDropdown = document.getElementById('aws-os');
    // const osTypeCheckboxes = document.querySelectorAll('input[name="os-type"]');
    const osDropdown = document.getElementById('aws-os');
    const amiDropdown = document.getElementById('aws-ami');
    const instanceTypeDropdown = document.getElementById('instance-type');
    const keyPairInput = document.getElementById('key-pair');
    const allowSSHCheckbox = document.getElementById('allow-ssh');
    const allowHTTPCheckbox = document.getElementById('allow-http');
    const storageInput = document.getElementById('ebs-storage');
    const dbTypeDropdown = document.getElementById('db-type');
    const phpVersionDropdown = document.getElementById('php-version');
    const webServerDropdown = document.getElementById('web-server');

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
        });
     });

    // Add event listener for form submission
    form.addEventListener('submit', async function(event) {
        try {
             // Prevent the default form submission behavior
            event.preventDefault();
            
            // Gather the form data
            const formData = new FormData(form);
            // Convert FormData to JSON object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            alert(JSON.stringify(data));
            const message = 'EC2 instance is being created.....'
            // alert(data);
            // updateStatusMessage(message);
            // Redirect to index.html with message as query parameter
            // window.location.href = '/index.html?message=' + encodeURIComponent(message);

            // Redirect to the main page
            window.location.href = '/';
          
            // Send the form data to the server
            
            const response = await fetch('/deploy-monolith', {
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

        try {
            const response = await fetch('/get-regions');
            const data = await response.json();
            console.log(`Consoling data, ${data}`);
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
            const response = await fetch(`/amis?region=${region}&os_type=${osType}`);
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
            const response = await fetch(`/instance-types?region=${region}&os_type=${osType}`);
            const data = await response.json();
            console.log(data.instance_types);
            return data.instance_types;
        } catch (error) {
            console.error('Error fetching instance types: ', error);
            return [];
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
            optionElement.textContent = `${option.RegionName}: ${option.Endpoint}`;
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
        allowSSHCheckbox.disabled = true;
        allowHTTPCheckbox.disabled = true;
        storageInput.disabled = true;
        dbTypeDropdown.disabled = true;
        phpVersionDropdown.disabled = true;
        webServerDropdown.disabled = true;
        // submitButton.disabled = true;

    }
});
 