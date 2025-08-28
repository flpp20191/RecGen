document.addEventListener('DOMContentLoaded', function() {
    // Automatically expand the recommendation card based on the cookie
    const clickedRecommendation = getCookie('clickedRecommendation');
    const clickedRecommendationTrue = getCookie('clickedRecommendationTrue');

    if (clickedRecommendation && clickedRecommendationTrue === 'true') {
        // Try to find the corresponding card by its ID
        const recommendationCard = document.getElementById('card-' + clickedRecommendation);

        if (recommendationCard) {
            // Expand the card
            const header = recommendationCard.querySelector('.card-header');
            toggleVisibility(header); 

            // Scroll the card into view
            recommendationCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Clear the cookies after they are used
        document.cookie = "clickedRecommendation=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "clickedRecommendationTrue=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    }

    // Add click event listeners to card headers to toggle their visibility
    const cardHeaders = document.querySelectorAll('.card-header');
    cardHeaders.forEach(header => {
        header.addEventListener('click', () => toggleVisibility(header));
    });

    // Scroll to the focused div if it exists
    const focusedDiv = document.getElementById('focused-div');
    if (focusedDiv) {
        focusedDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});

function toggleVisibility(header) {
    const nestedTable = header.nextElementSibling;
    const icon = header.querySelector('.bi');
    if (icon) {
        icon.classList.toggle('bi-plus-circle');
        icon.classList.toggle('bi-dash-circle');
        nestedTable.style.display = nestedTable.style.display === 'block' ? 'none' : 'block';
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) return decodeURIComponent(value);
        }
    }
    return cookieValue;
}
