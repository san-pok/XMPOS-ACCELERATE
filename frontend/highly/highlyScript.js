$(document).ready(function () {
    const regionSelect = $('#region');
    const osSelect = $('#os_type');
    const instanceTypeSelect = $('#instance_type');
    const amiTypeSelect = $('#search_ami_type');
    const deployForm = $('#deployForm');
    const formInputs = deployForm.find('input, select, button');
    const $searchInstanceInput = $('#search_instance_type');
    const $searchAmiInput = $('#search_ami_type');
    const $dropdownInstanceContainer = $('#instanceTypeDropdown');
    const $dropdownAmiContainer = $('#amiTypeDropdown');

    let instanceTypes = [];
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

    // Fetch regions and populate the region select dropdown when DOM content is loaded
    fetchRegionsAndPopulate();
});
