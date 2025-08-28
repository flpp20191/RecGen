document.addEventListener("DOMContentLoaded", function() {
    // Function to set custom messages
    function setCustomMessages(element) {
      const fieldType = element.getAttribute("type");
      switch (fieldType) {
        case "email":
          element.setCustomValidity("Lūdzu, ievadiet derīgu e-pasta adresi.");
          break;
        case "password":
          element.setCustomValidity("Lūdzu, ievadiet paroli.");
          break;
        // Add more cases as needed
        default:
          element.setCustomValidity("Šis lauks ir obligāts.");
          break;
      }
  
      // Reset custom validity message when the user corrects the input
      element.addEventListener("input", function() {
        element.setCustomValidity("");
      });
    }
  
    // Apply custom messages to all forms on the page
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
      const inputs = form.querySelectorAll("input, select, textarea");
      inputs.forEach(input => {
        input.addEventListener("invalid", function() {
          setCustomMessages(input);
        });
      });
    });
  });
  