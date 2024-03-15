document.addEventListener('DOMContentLoaded', async function() {
    const regionDropdown = document.getElementById('lightsail-region');
    const platformRadioButtons = document.getElementsByName('platform');
    const blueprintDropdown = document.getElementById('lightsail-blueprint');
    const bundleDropdown = document.getElementById('lightsail-bundle');
    const form = document.getElementById('lightsail-deployment-form');

     // Disable platform radio buttons and blueprint dropdown initially
     platformRadioButtons.forEach(radioButton => {
        radioButton.disabled = true;
    });
    blueprintDropdown.disabled = true;
    bundleDropdown.disabled = true;

    // Populate dropdown with regions
    const lightsailRegions = await fetchLightsailRegions();
    populateDropdownRegion(regionDropdown, lightsailRegions);

    // Attach event listener to region dropdown for change events
    regionDropdown.addEventListener('change', async function(){
        // Fetch blueprints for the selected region
        const selectedRegion = regionDropdown.value;
        // Enable platform radio buttons
        platformRadioButtons.forEach(radioButton => {
            radioButton.disabled = false;
        });
        const selectedPlatform = getSelectedPlatform();
        if(selectedRegion && selectedPlatform){
            blueprintDropdown.disabled = false; // Enable blueprint dropdown
            blueprintDropdown.innerHTML = ''; // Clear previous options
            const blueprints = await fetchBlueprints(selectedRegion, selectedPlatform);
            console.log('Blueprints: ',blueprints)
            populateDropdownBlueprint(blueprintDropdown, blueprints);
        }
    });

     // Attach event listener to blueprint dropdown for change events
     blueprintDropdown.addEventListener('change', async function(){
        // const selectedBlueprint = blueprintDropdown.value;
        // Fetch blueprints for the selected region
        const selectedRegion = regionDropdown.value;
        const selectedPlatform = getSelectedPlatform();
        if(selectedPlatform){
            // Enable bundle dropdown
            bundleDropdown.disabled = false;
            // Fetch instance plans for the selected blueprint 
            const instancePlans = await fetchInstancePlans(selectedPlatform, selectedRegion);
            populateDropdownBundles(bundleDropdown, instancePlans);
        }
    });

    // Attach event listener to platform radio buttons for change events
    platformRadioButtons.forEach(button => {
        button.addEventListener('change', async function(){
            const selectedPlatform = getSelectedPlatform();
            if(selectedPlatform){
                const selectedRegion = regionDropdown.value;
                const blueprints = await fetchBlueprints(selectedRegion, selectedPlatform);
                populateDropdownBlueprint(blueprintDropdown, blueprints);
            }
        });
    });

     // Function to fetch lightsail regions
     async function fetchLightsailRegions(){
        try {
            const response = await fetch('/lightsail-regions');
            // console.log(response);
            const data = await response.json();
            console.log(`fetched data in /lightsail-regions: ${data}`);
            return data.regions;
        } catch (error){
            console.error('Error fetching lightsail regions: ', error);
            return[];
        }
    }

    // Function to fetch blueprints for a region
    async function fetchBlueprints(region, platform){
        try{
            const response = await fetch(`/lightsail-blueprints?region=${region}&platform=${platform}`);
            const data = await response.json();
            return data.blueprints;
        } catch (error){
            console.error('Error fetching blueprints: ', error);
            return [];
        }
    }

    // Function to fetch instance plan (bundle_id) for a blueprint
    async function fetchInstancePlans(selectedPlatform, selectedRegion){
        try{
            const response = await fetch(`/lightsail-instance-plans?platform=${selectedPlatform}&region=${selectedRegion}`);
            const data = await response.json();
            return data.bundles;
        } catch (error){
            console.error('Error fetching bundle_id or instance plan: ', error);
            return [];
        }
    }

    function populateDropdownRegion(dropdown, options){
        dropdown.innerHTML='';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = `Select a Region`;
        dropdown.appendChild(placeholderOption)

        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.name;
            optionElement.textContent = `${option.displayName}: ${option.name}`;
            dropdown.appendChild(optionElement);
        });
    }  

    function populateDropdownBlueprint(dropdown, options){
        dropdown.innerHTML='';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = `Select a Blueprint`;
        dropdown.appendChild(placeholderOption)

        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.id;
            optionElement.textContent = `${option.displayName}: ${option.id} :${option.type}`;
            dropdown.appendChild(optionElement);
        });
    } 

    function populateDropdownBundles(dropdown, options){
        dropdown.innerHTML='';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = `Select a Plan`;
        dropdown.appendChild(placeholderOption)

        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.id;
            optionElement.textContent = `PRICE: ${option.displayPrice} per month - CPU: ${option.cpuCount}, RAM: ${option.ramSizeInGb} GB, Disk: ${option.diskSizeInGb} GB, Transfer: ${option.transferPerMonthInGb} GB`;
            dropdown.appendChild(optionElement);
        });
    } 

    // Function to get selected platform
    function getSelectedPlatform(){
        for(let i=0; i < platformRadioButtons.length; i++){
            if(platformRadioButtons[i].checked){
                console.log('Selected Platform Value: ',platformRadioButtons[i].value);
                return platformRadioButtons[i].value;
            }
        }
        return null;
    }



    // Add event listener for form submission
    form.addEventListener('submit', async function(event) {
        try {
             // Prevent the default form submission behavior
            event.preventDefault();
            // // Gather the form data
            const formData = new FormData(form);
            // // Convert FormData to JSON object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            alert(JSON.stringify(data));
            
            // Redirect to the main page
            window.location.href = '/';
            // Reload the page after a short delay
           
            // Send the form data to the server
            const response = await fetch('/deploy-lightsail', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
                
            })
            // Reload the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1000); // Refresh after 1 seconds (adjust as needed)
        } catch (error){
            console.error('Error on submitting forms for Monolith deployment ', error);
        }

    });

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
});
