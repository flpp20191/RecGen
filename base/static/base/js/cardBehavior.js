document.addEventListener("DOMContentLoaded", function () {
  var cardHeaders = document.querySelectorAll(".dashboard-card-header-clickable");

  cardHeaders.forEach(function (header) {
      header.addEventListener("click", function () {
          var nestedTable = this.nextElementSibling;
          var icon = this.querySelector(".bi");

          if (nestedTable.style.display === "none" || nestedTable.style.display === "") {
              icon.classList.remove("bi-plus-circle");
              icon.classList.add("bi-dash-circle");
              nestedTable.style.display = "block";
          } else {
              icon.classList.remove("bi-dash-circle");
              icon.classList.add("bi-plus-circle");
              nestedTable.style.display = "none";
          }
      });
  });
});
