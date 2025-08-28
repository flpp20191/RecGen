document.addEventListener('DOMContentLoaded', function() {
    const categories = document.querySelectorAll('[id^="chart-"]');
    categories.forEach((chartElement) => {
        const categoryId = chartElement.id.split('-')[1];
        const percentageElement = document.getElementById(`data-${categoryId}`);
        if (percentageElement) {
            let averageValue = parseFloat(percentageElement.textContent);
    
            // Handle NaN value by setting it to 0
            if (isNaN(averageValue)) {
                averageValue = 0;
            }
    
            // Determine gauge color based on value
            var gaugeColor;
            if (averageValue < 33) {
                gaugeColor = '#dc3545'; // Red
            } else if (averageValue < 66) {
                gaugeColor = '#ffc107'; // Yellow
            } else {
                gaugeColor = '#198754'; // Green
            }
    
            // Function to calculate luminance
            function getLuminance(color) {
                const rgb = parseInt(color.slice(1), 16); 
                const r = (rgb >> 16) & 0xff;
                const g = (rgb >> 8) & 0xff;
                const b = (rgb >> 0) & 0xff;
                return 0.2126 * r + 0.7152 * g + 0.0722 * b;
            }
    
            // Determine text color based on luminance and special conditions
            let textColor;
            if (averageValue === 0) {
                textColor = '#000000'; 
            } else if (averageValue <= 20) {
                textColor = '#0000FF';
            } else {
                const luminance = getLuminance(gaugeColor);
                textColor = luminance > 128 ? '#000000' : '#FFFFFF'; 
            }
    
            // Determine offsetX based on the percentage value
            let offsetX;
            if (averageValue === 0) {
                offsetX = 20; 
            } else if (averageValue < 20) {
                offsetX = 40; 
            } else {
                offsetX = 10; 
            }
    
            var options = {
                series: [{
                    data: [averageValue]
                }],
                chart: {
                    type: 'bar',
                    height: 30,
                    width: '100%',
                    sparkline: {
                        enabled: true
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        barHeight: '100%',
                        colors: {
                            ranges: [{
                                from: 0,
                                to: 32,
                                color: '#dc3545' 
                            }, {
                                from: 33,
                                to: 65,
                                color: '#ffc107' 
                            }, {
                                from: 66,
                                to: 100,
                                color: '#198754' 
                            }]
                        }
                    }
                },
                dataLabels: {
                    enabled: true,
                    formatter: function (val) {
                        return parseFloat(val).toFixed(2) + '%';
                    },
                    style: {
                        colors: [textColor],
                        fontSize: '14px',
                        fontWeight: 'bold'
                    },
                    offsetX: offsetX
                },
                fill: {
                    colors: [gaugeColor]
                },
                labels: ['Percent'],
                tooltip: {
                    enabled: false
                },
                xaxis: {
                    min: 0,
                    max: 100
                }
            };
    
            var chart = new ApexCharts(chartElement, options);
            chart.render();
        }
    });
    

    const eyeIcons = document.querySelectorAll('.eye-icon');
    eyeIcons.forEach(icon => {
        icon.addEventListener('click', function(event) {
            const categoryId = this.dataset.categoryId;
            document.cookie = `clickedAuditRecommendation=${categoryId}; path=/`;
            document.cookie = `clickedAuditRecommendationTrue=true; path=/`;
        });
    });

    const cardHeaders = document.querySelectorAll('.card-header');
    cardHeaders.forEach(header => {
        header.addEventListener('click', () => toggleVisibility(header));
    });

    const clickedAuditRecommendation = getCookie('clickedAuditRecommendation');
    const clickedAuditRecommendationTrue = getCookie('clickedAuditRecommendationTrue');
    if (clickedAuditRecommendation && clickedAuditRecommendationTrue === 'true') {
        const AuditRecommendationElement = document.getElementById('card-category-' + clickedAuditRecommendation);
        if (AuditRecommendationElement) {
            const header = AuditRecommendationElement.querySelector('.card-header');
            toggleVisibility(header); 
            AuditRecommendationElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            document.cookie = "clickedAuditRecommendationTrue=false; path=/";
    }
    
    // Clear cookies after they are used
    document.cookie = "clickedAuditRecommendation=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "clickedAuditRecommendationTrue=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

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


