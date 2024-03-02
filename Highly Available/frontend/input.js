
document.getElementById("myForm").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent the default form submission


  var formData = new FormData(this);

  // Convert form data to JSON object
  var jsonObject = {};
  formData.forEach(function(value, key){
    jsonObject[key] = value;
  });

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

function displaySuccessMessage(message) {

  var successMessageElement = document.getElementById("successMessage");
  successMessageElement.innerText = message;
  successMessageElement.style.display = "block";


  var errorMessageElement = document.getElementById("errorMessage");
  errorMessageElement.style.display = "none";
}

function displayErrorMessage(error) {

  var errorMessageElement = document.getElementById("errorMessage");
  errorMessageElement.innerText = error;
  errorMessageElement.style.display = "block";


  var successMessageElement = document.getElementById("successMessage");
  successMessageElement.style.display = "none";
}
