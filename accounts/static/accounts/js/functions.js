document.addEventListener("DOMContentLoaded", function() {

    // Function to toggle all checkboxes
    const selectAllCheckbox = document.getElementById("categories-select-all");
    if (selectAllCheckbox) {
      const categoryCheckboxes = document.querySelectorAll(".categories-checkbox");
      selectAllCheckbox.addEventListener("click", function() {
        categoryCheckboxes.forEach(checkbox => {
          checkbox.checked = this.checked;
        });
      });
  
      categoryCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("click", () => {
          const allChecked = Array.from(categoryCheckboxes).every(c => c.checked);
          selectAllCheckbox.checked = allChecked;
        });
      });
    }    
     // Attaching event listeners to each toggle icon
     attachPasswordToggle('toggleOldPassword', 'id_old_password');
     attachPasswordToggle('toggleNewPassword1', 'id_new_password1');
     attachPasswordToggle('toggleNewPassword2', 'id_new_password2');

    function attachPasswordToggle(toggleIconId, inputId) {
        var toggleIcon = document.getElementById(toggleIconId);
        if (toggleIcon) {
          toggleIcon.addEventListener('click', function() {
            togglePassword(inputId, toggleIconId);
          });
        }
    }
      
    function togglePassword(inputId, toggleIconId) {
        var input = document.getElementById(inputId);
        var icon = document.getElementById(toggleIconId);
        
        if (input && input.type === 'password') {
          input.type = 'text';
          icon.classList.remove('bi-eye-slash-fill');
          icon.classList.add('bi-eye-fill');
        } else if (input) {
          input.type = 'password';
          icon.classList.remove('bi-eye-fill');
          icon.classList.add('bi-eye-slash-fill');
        }
    }
  });
