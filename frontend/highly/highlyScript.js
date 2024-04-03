$(document).ready(function () {
    const regionSelect = $('#region');
    const osSelect = $('#os_type');
    const instanceTypeSelect = $('#instance_type');
    const dbEngineSelect = $('#search_db_engine');
    const dbEngineVersion = $('#search_engine_version');
    const amiTypeSelect = $('#search_ami_type');
    const deployForm = $('#deployForm');
    const formInputs = deployForm.find('input, select, button');
    const $searchInstanceInput = $('#search_instance_type');
    const $searchDbEngine = $('#search_db_engine');
    const $searchEngineVersion = dbEngineVersion;
    const $searchAmiInput = $('#search_ami_type');
    const $dropdownInstanceContainer = $('#instanceTypeDropdown');
    const $dropDbEngineContainer = $('#dbEngineDropDown');
    const $dropEngineVersionContainer = $('#engineVersionDropDown');
    const $dropdownAmiContainer = $('#amiTypeDropdown');
    const keyPairSelection = $('input[name="key_pair_selection"]');
    const existingKeyPairsContainer = $('#existingKeyPairsContainer');
    const existingKeyPairSelect = $('#existing_key_pair');

    let instanceTypes = [];
    let dbEngineList = [];
    let engineVersionList = [];
    let amiList = [];
    let regions = [];

    // Fetch instance types based on region
    function fetchInstanceTypesAndPopulate(region) {
        if (!region) {
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/highly/instance_types',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: { region: encodeURIComponent(region) },
            success: function (data) {
                instanceTypes = data;
                populateInstanceTypeSelect();
            },
            error: function (error) {
                console.error('Error fetching instance types:', error);
            }
        });
    }

    // Populate instance type select dropdown
    function populateInstanceTypeSelect() {
        instanceTypeSelect.empty();

        instanceTypes.forEach(type => {
            const option = $('<option>', { value: type, text: type });
            instanceTypeSelect.append(option);
        });
    }

    function fetchDbEnginesAndPopulate(region) {
        if (!region) {
            return;
        }

        $.ajax({
            url: 'http://127.0.0.1:5000/highly/db_engine_types',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: { region: encodeURIComponent(region) },
            success: function (data) {
                dbEngineList = data;
                populateDbEngineSelect();
            },
            error: function (error) {
                console.error('Error fetching Db Engine types:', error);
            }
        });
    }


    function populateDbEngineSelect() {
        dbEngineSelect.empty();

        dbEngineList.forEach(type => {
            const option = $('<option>', { value: type, text: type });
            dbEngineSelect.append(option);
        });
    }

    function fetchEngineVersionsAndPopulate(region,engine) {

        $.ajax({
            url: 'http://127.0.0.1:5000/highly/db_engine_versions',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: { region: encodeURIComponent(region), engine: engine },
            success: function (data) {
                engineVersionList = data;
                populateEngineVersionSelect();
            },
            error: function (error) {
                console.error('Error fetching Db Engine Version types:', error);
            }
        });
    }

    function populateEngineVersionSelect() {
        dbEngineVersion.empty();

        engineVersionList.forEach(type => {
            const option = $('<option>', { value: type, text: type });
            dbEngineVersion.append(option);
        });
    }

    // Fetch AMI types based on region and OS type
    function fetchAmisAndPopulate(region, osType) {
        $.ajax({
            url: 'http://127.0.0.1:5000/highly/amis',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: { region: encodeURIComponent(region), os_type: osType },
            success: function (data) {
                amiList = data;
                populateAmiSelect();
            },
            error: function (error) {
                console.error('Error fetching AMI types:', error);
            }
        });
    }

    // Populate AMI type input with filtered options
    function populateAmiSelect() {
        amiTypeSelect.empty();

        amiList.forEach(ami => {
            const option = $('<option>', { value: ami.ImageId, text: ami.ImageId });
            amiTypeSelect.append(option);
        });
    }

    // Fetch regions and populate the region select dropdown
    function fetchRegionsAndPopulate() {
        $.ajax({
            url: 'http://127.0.0.1:5000/highly/get_regions',
            method: 'GET',
            success: function (data) {
                regions = data;
                populateRegionSelect();
            },
            error: function (error) {
                console.error('Error fetching regions:', error);
            }
        });
    }

    // Populate region select dropdown with available regions
    function populateRegionSelect() {
        regionSelect.empty();

        regions.forEach(region => {
            const option = $('<option>', { value: region, text: region });
            regionSelect.append(option);
        });
    }

    // Disable all form inputs except region select
    formInputs.each(function () {
        if (!$(this).is(regionSelect)) {
            $(this).prop('disabled', true);
        }
    });

    // Enable form inputs and fetch instance types when region is selected
    regionSelect.on('change', function () {
        const selectedRegion = $(this).val();
        formInputs.prop('disabled', false);
        fetchInstanceTypesAndPopulate(selectedRegion);
        const osType = $('#os_type').val();
        fetchAmisAndPopulate(selectedRegion, osType);
        fetchDbEnginesAndPopulate(selectedRegion);
    });

    osSelect.on('change', function () {
        const selectedOs = $(this).val();
        const selectedRegion = regionSelect.val();

        fetchAmisAndPopulate(selectedRegion, selectedOs);
    });

    // Event listener for search input for instance types
    $searchInstanceInput.on('input', function () {
        const searchText = $(this).val().trim();
        createDropdownOptions(searchText);
    });

    // Event listener for search input for AMI types
    $searchAmiInput.on('input', function () {
        const searchText = $(this).val().trim();
        createAmiDropdownOptions(searchText);
    });

    $searchDbEngine.on('input', function () {
        const searchText = $(this).val().trim();
        createDbEngineDropdown(searchText);
    });

    $searchEngineVersion.on('input', function () {
        const searchText = $(this).val().trim();
        createEngineVersionDropdown(searchText);
    });

    // Function to create dropdown options based on search input for instance types
    function createDropdownOptions(searchText) {
        const filteredTypes = instanceTypes.filter(type =>
            type.toLowerCase().includes(searchText.toLowerCase())
        );
        $dropdownInstanceContainer.empty();

        filteredTypes.forEach(type => {
            const $option = $('<div>', { class: 'dropdown-option', text: type });
            $option.on('click', function () {
                $searchInstanceInput.val(type);
                $dropdownInstanceContainer.empty();
            });
            $dropdownInstanceContainer.append($option);
        });

        if (searchText.trim() !== '') {
            $dropdownInstanceContainer.removeClass('hidden');
        } else {
            $dropdownInstanceContainer.addClass('hidden');
        }
    }

    function createDbEngineDropdown(searchText) {
        const filteredDbEngines = dbEngineList.filter(type =>
            type.toLowerCase().includes(searchText.toLowerCase())
        );
        $dropDbEngineContainer.empty();

        filteredDbEngines.forEach(type => {
            const $option = $('<div>', { class: 'dropdown-option', text: type });
            $option.on('click', function () {
                $searchDbEngine.val(type);
                const selectedRegion = regionSelect.val();

                fetchEngineVersionsAndPopulate(selectedRegion,type);
                $dropDbEngineContainer.empty();


            });
            $dropDbEngineContainer.append($option);
        });

        if (searchText.trim() !== '') {
            $dropDbEngineContainer.removeClass('hidden');
        } else {
            $dropDbEngineContainer.addClass('hidden');
        }
    }

    function createEngineVersionDropdown(searchText) {
        const filteredEngineVersions = engineVersionList.filter(type =>
            type.toLowerCase().includes(searchText.toLowerCase())
        );
        $dropEngineVersionContainer.empty();

        filteredEngineVersions.forEach(type => {
            const $option = $('<div>', { class: 'dropdown-option', text: type });
            $option.on('click', function () {
                $searchEngineVersion.val(type);
                $dropEngineVersionContainer.empty();
            });
            $dropEngineVersionContainer.append($option);
        });

        if (searchText.trim() !== '') {
            $dropEngineVersionContainer.removeClass('hidden');
        } else {
            $dropEngineVersionContainer.addClass('hidden');
        }
    }

    // Function to create dropdown options based on search input for AMI types
    function createAmiDropdownOptions(searchText) {
        const filteredAmis = amiList.filter(ami =>
            ami.ImageId.toLowerCase().includes(searchText.toLowerCase())
        );
        $dropdownAmiContainer.empty();

        filteredAmis.forEach(ami => {
            const $option = $('<div>', { class: 'dropdown-option', text: ami.ImageId });
            $option.on('click', function () {
                $searchAmiInput.val(ami.ImageId);
                $dropdownAmiContainer.empty();
            });
            $dropdownAmiContainer.append($option);
        });

        if (searchText.trim() !== '') {
            $dropdownAmiContainer.removeClass('hidden');
        } else {
            $dropdownAmiContainer.addClass('hidden');
        }
    }

    // Event listener for clearing the instance type dropdown on click outside
    $(document).on('click', function (e) {
        if (!$dropdownInstanceContainer.is(e.target) && $dropdownInstanceContainer.has(e.target).length === 0) {
            $dropdownInstanceContainer.addClass('hidden');
        }
    });

    // Event listener for clearing the AMI dropdown on click outside
    $(document).on('click', function (e) {
        if (!$dropdownAmiContainer.is(e.target) && $dropdownAmiContainer.has(e.target).length === 0) {
            $dropdownAmiContainer.addClass('hidden');
        }
    });

    // Event listener for clearing the db Engine type dropdown on click outside
    $(document).on('click', function (e) {
        if (!$dropDbEngineContainer.is(e.target) && $dropDbEngineContainer.has(e.target).length === 0) {
            $dropDbEngineContainer.addClass('hidden');
        }
    });

    // Event listener for clearing the Engine Version type dropdown on click outside
    $(document).on('click', function (e) {
        if (!$dropEngineVersionContainer.is(e.target) && $dropEngineVersionContainer.has(e.target).length === 0) {
            $dropEngineVersionContainer.addClass('hidden');
        }
    });

    // Event listener for key pair selection radio buttons
    keyPairSelection.on('change', function () {
        const selectedValue = $(this).val();
        if (selectedValue === 'create') {
            $('#newKeyPairContainer').removeClass('hidden');
            existingKeyPairsContainer.addClass('hidden');
        } else if (selectedValue === 'existing') {
            $('#newKeyPairContainer').addClass('hidden');
            existingKeyPairsContainer.removeClass('hidden');
            fetchExistingKeyPairs();
        }
    });

    // Event listener for creating a new key pair
    $('#createNewKeyPairBtn').on('click', function () {
        const newKeyPairName = $('#new_key_pair_name').val().trim();
        if (newKeyPairName) {
            createNewKeyPair(newKeyPairName);
        } else {
            alert('Please enter a key pair name.');
        }
    });

    // Function to create a new key pair (you can replace this with your actual API call)
    function createNewKeyPair(newKeyPairName) {
        event.preventDefault();
        $.ajax({
            url: 'http://127.0.0.1:5000/highly/create_key_pair',
            method: 'POST',
            data: { new_key_pair_name: newKeyPairName },
            success: function (data) {
                alert(data.message);
            },
            error: function (error) {
                alert('Error creating key pair: ' + error);
            }
        });
    }

    // Function to fetch existing key pairs based on region
    function fetchExistingKeyPairs() {
        const selectedRegion = $('#region').val();
        $.ajax({
            url: 'http://127.0.0.1:5000/highly/existing_key_pairs',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: { region: encodeURIComponent(selectedRegion) },
            success: function (data) {
                populateExistingKeyPairs(data);
            },
            error: function (error) {
                console.error('Error fetching existing key pairs:', error);
            }
        });
    }

    // Populate existing key pairs dropdown
    function populateExistingKeyPairs(data) {
        existingKeyPairSelect.empty();
        const keyPairs = data.existing_key_pairs;

        keyPairs.forEach(keyPair => {
            const option = $('<option>', { value: keyPair, text: keyPair });
            existingKeyPairSelect.append(option);
        });
    }

    // Fetch regions and populate the region select dropdown when DOM content is loaded
    fetchRegionsAndPopulate();

    $('#deployForm').on('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission behavior

        const formData = $(this).serializeArray();

        // Manually replace values for dynamically populated inputs if they exist
        replaceFormDataValue(formData, 'ami_type', $('#search_ami_type').val());
        replaceFormDataValue(formData, 'instance_type', $('#search_instance_type').val());
        replaceFormDataValue(formData, 'db_engine', $('#search_db_engine').val());
        replaceFormDataValue(formData, 'engine_version', $('#search_engine_version').val());

        // Convert formData to JSON format
        const jsonData = JSON.stringify(formData);

        console.log(jsonData)

        // Send an AJAX request to your API endpoint

        $.ajax({
            url: 'http://127.0.0.1:5000/highly/validate_form',
            method: 'POST',
            data: jsonData,
            contentType: 'application/json', // Set the Content-Type header to JSON
            success: function (response) {
                console.log('Form validation successful:', response);
                // You can handle the success response here, such as showing a success message to the user
                alert('Form validation successful and infrastructure deployment triggered');
            },
            error: function (error) {
                console.error('Error validating form:', error);
                // You can handle the error response here, such as showing an error message to the user
                alert('Error validating form. Please try again.');
            }
        });

    });

    function replaceFormDataValue(formData, key, value) {
        const index = formData.findIndex(item => item.name === key);
        if (index !== -1) {
            formData[index].value = value;
        } else {
            formData.push({ name: key, value: value });
        }
    }

});
