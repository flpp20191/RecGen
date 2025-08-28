document.addEventListener("DOMContentLoaded", function () {
    var isTierOne = document.querySelector('meta[name="is_tier_one"]').content === 'true';
    var isTierTwo = document.querySelector('meta[name="is_tier_two"]').content === 'true';
    var isTierThree = document.querySelector('meta[name="is_tier_three"]').content === 'true';

    if (isTierOne) {
        let nestedTable1 = document.getElementById("nested-table-1");
        let icon1 = document.querySelector("#card-header-1 .bi");
        icon1.classList.remove("bi-plus-circle");
        icon1.classList.add("bi-dash-circle");
        nestedTable1.style.display = "block";
    }

    if (isTierTwo) {
        let nestedTable2 = document.getElementById("nested-table-2");
        let icon2 = document.querySelector("#card-header-2 .bi");
        icon2.classList.remove("bi-plus-circle");
        icon2.classList.add("bi-dash-circle");
        nestedTable2.style.display = "block";
    }

    if (isTierThree) {
        let nestedTable3 = document.getElementById("nested-table-3");
        let icon3 = document.querySelector("#card-header-3 .bi");
        icon3.classList.remove("bi-plus-circle");
        icon3.classList.add("bi-dash-circle");
        nestedTable3.style.display = "block";
    }
});
