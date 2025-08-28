document.addEventListener('DOMContentLoaded', function() {
    var averageValue = document.querySelector('meta[name="average_value"]').content;
    averageValue = parseFloat(averageValue);

    // Handle NaN values by setting a default value, e.g., 0
    if (isNaN(averageValue)) {
        averageValue = 0;
    }

    var gaugeColor;
    if (averageValue < 33) {
        gaugeColor = '#dc3545'; // Red
    } else if (averageValue < 66) {
        gaugeColor = '#ffc107'; // Yellow
    } else {
        gaugeColor = '#198754'; // Green
    }

    var options = {
        series: [averageValue],
        chart: {
            type: 'radialBar',
            height: 450,
            background: '#FFF'
        },
        plotOptions: {
            radialBar: {
                startAngle: -135,
                endAngle: 135,
                hollow: {
                    margin: 5,
                    size: '50%',
                    background: 'transparent',
                },
                track: {
                    background: '#f2f2f2',
                    strokeWidth: '50%',
                },
                dataLabels: {
                    name: {
                        show: false
                    },
                    value: {
                        fontSize: '24px',
                        offsetY: 120,
                        formatter: function (val) {
                            return parseFloat(val).toFixed(2) + '%';
                        }
                    }
                }
            }
        },
        fill: {
            colors: [gaugeColor]
        },
        labels: ['Percent']
    };

    var chart = new ApexCharts(document.querySelector("#chart"), options);
    chart.render();
});
