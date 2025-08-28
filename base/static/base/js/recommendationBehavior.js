document.addEventListener('DOMContentLoaded', function () {
    var eyeIcons = document.querySelectorAll('.bi-eye-fill');

    eyeIcons.forEach(function (icon) {
        icon.addEventListener('click', function (event) {
            var recommendationId = event.target.getAttribute('data-id');
            document.cookie = "clickedRecommendation=" + recommendationId + "; path=/";
            document.cookie = "clickedRecommendationTrue=true; path=/";
        });
    });
});