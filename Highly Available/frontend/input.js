// Define the populateExistingKeyPairs function
function populateExistingKeyPairs() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/existing_key_pairs", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    var existingKeyPairsDropdown = document.getElementById("existing_key_pair_name");
                    existingKeyPairsDropdown.innerHTML = ""; // Clear existing options
                    if (response && response.existing_key_pairs && Array.isArray(response.existing_key_pairs)) {
                        response.existing_key_pairs.forEach(function(keyPair) {
                            var option = document.createElement("option");
                            option.value = keyPair;
                            option.text = keyPair;
                            existingKeyPairsDropdown.appendChild(option);
                        });
                    } else {
                        console.error("Existing key pairs not found or not in the expected format.");
                    }
                } catch (error) {
                    console.error("Error parsing server response:", error);
                }
            } else {
                console.error("Failed to fetch existing key pairs. Server returned status:", xhr.status);
            }
        }
    };
    xhr.send();
}


// Populate existing key pairs dropdown menu when the page loads
window.addEventListener('DOMContentLoaded', function() {
    populateExistingKeyPairs();
});

// Define the event listener for radio button change
document.querySelectorAll('input[name="key_pair_selection"]').forEach(function(radio) {
    radio.addEventListener('change', function() {
        var existingKeyPairSection = document.getElementById("existing_key_pair");
        var newKeyPairSection = document.getElementById("new_key_pair");

        if (this.value === "existing") {
            existingKeyPairSection.style.display = "block";
            newKeyPairSection.style.display = "none";
        } else {
            newKeyPairSection.style.display = "block";
            existingKeyPairSection.style.display = "none";
        }
    });
});

// Define the form submission handling
document.getElementById("myForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the default form submission

    var formData = new FormData(this);

    // Convert form data to JSON object
    var jsonObject = {};
    formData.forEach(function(value, key) {
        jsonObject[key] = value;
    });

      // If the user chose to create a new key pair, include the new key pair name in the JSON object
      if (document.getElementById("new_key_pair_radio").checked) {
        delete jsonObject['existing_key_pair_name']; // Remove the existing key pair field
      }else{
        delete jsonObject['new_key_pair_name']; // Remove the new key pair field

      }
    console.log(jsonObject);

    // Send form data to Flask server for validation
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/validate_form", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                displaySuccessMessage(response.message);
            } else {
                var errorResponse = JSON.parse(xhr.responseText);
                displayErrorMessage(errorResponse.error);
            }
        }
    };
    xhr.send(JSON.stringify(jsonObject));
});

// Define the function to display success message
function displaySuccessMessage(message) {
    var successMessageElement = document.getElementById("successMessage");
    successMessageElement.innerText = message;
    successMessageElement.style.display = "block";

    var errorMessageElement = document.getElementById("errorMessage");
    errorMessageElement.style.display = "none";
}

// Define the function to display error message
function displayErrorMessage(error) {
    var errorMessageElement = document.getElementById("errorMessage");
    errorMessageElement.innerText = error;
    errorMessageElement.style.display = "block";

    var successMessageElement = document.getElementById("successMessage");
    successMessageElement.style.display = "none";
}
