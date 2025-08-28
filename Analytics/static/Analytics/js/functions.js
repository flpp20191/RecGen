document.addEventListener('DOMContentLoaded', function () {
    // Code for categories and questions checkboxes (for analyst pages)
    const categoriesCheckboxes = document.querySelectorAll('.categories-checkbox-analyst');
    const questionCheckboxes = document.querySelectorAll('.question-checkbox-analyst');

    if (categoriesCheckboxes.length > 0 && questionCheckboxes.length > 0) {
        categoriesCheckboxes.forEach(categoryCheckbox => {
            categoryCheckbox.addEventListener('change', function () {
                const categoryId = this.value;
                questionCheckboxes.forEach(questionCheckbox => {
                    if (questionCheckbox.dataset.category === categoryId) {
                        questionCheckbox.checked = this.checked;
                    }
                });
            });
        });
    }

    // Code for handling the nested tables (for dashboard or user detail pages)
    const cardHeaders = document.querySelectorAll(".dashboard-card-header-clickable");
    const nestedTable1 = document.getElementById("nested-table-1");
    const nestedTable2 = document.getElementById("nested-table-2");
    const nestedTable3 = document.getElementById("nested-table-3");

    // if (cardHeaders.length > 0) {
    //     if (nestedTable1 && nestedTable2 && nestedTable3) {
    //         let icon1 = document.querySelector("#card-header-1 .bi");
    //         let icon2 = document.querySelector("#card-header-2 .bi");
    //         let icon3 = document.querySelector("#card-header-3 .bi");

    //         icon1.classList.add("bi-dash-circle");
    //         nestedTable1.style.display = "block";

    //         icon2.classList.add("bi-dash-circle");
    //         nestedTable2.style.display = "block";

    //         icon3.classList.add("bi-dash-circle");
    //         nestedTable3.style.display = "block";

    //         cardHeaders.forEach(function (header) {
    //             header.addEventListener("click", function () {
    //                 var nestedTable = this.nextElementSibling;
    //                 var icon = this.querySelector(".bi");

    //                 if (nestedTable.style.display === "none" || nestedTable.style.display === "") {
    //                     icon.classList.remove("bi-plus-circle");
    //                     icon.classList.add("bi-dash-circle");
    //                     nestedTable.style.display = "block";
    //                 } else {
    //                     icon.classList.remove("bi-dash-circle");
    //                     icon.classList.add("bi-plus-circle");
    //                     nestedTable.style.display = "none";
    //                 }
    //             });
    //         });
    //     }
    // }


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
    // Code for rendering charts (for summary page)
    const schoolDataElement = document.getElementById('userData');
    if (schoolDataElement) {
        const schoolData = JSON.parse(schoolDataElement.textContent);
        schoolData.forEach((user, index) => {
            const averageValue = parseFloat(user.average_value);
            var gaugeColor;
            if (averageValue < 33) {
                gaugeColor = '#dc3545';
            } else if (averageValue < 66) {
                gaugeColor = '#ffc107'; 
            } else {
                gaugeColor = '#198754'; 
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
                                color: '#dc3545' // Red
                            }, {
                                from: 33,
                                to: 65,
                                color: '#ffc107' // Yellow
                            }, {
                                from: 66,
                                to: 100,
                                color: '#198754' // Green
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
                        colors: ['#fff'],
                        fontSize: '14px',
                        fontWeight: 'bold'
                    },
                    offsetX: 10
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

            var chart = new ApexCharts(document.querySelector(`#chart-${index}`), options);
            chart.render();
        });

        const languageSettings = {
            en: {
                "decimal": ".",
                "emptyTable": "No data available in table",
                "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                "infoEmpty": "Showing 0 to 0 of 0 entries",
                "infoFiltered": "(filtered from _MAX_ total entries)",
                "lengthMenu": "Show _MENU_ entries",
                "loadingRecords": "Loading...",
                "processing": "Processing...",
                "search": "Search:",
                "zeroRecords": "No matching records found",
                "paginate": {
                    "first": "First",
                    "last": "Last",
                    "next": "Next",
                    "previous": "Previous"
                },
                "aria": {
                    "sortAscending": ": activate to sort column ascending",
                    "sortDescending": ": activate to sort column descending"
                }
            }
        };

        $('#userTable').DataTable({
            "paging": true,
            "searching": true,
            "ordering": true,
            "order": [[0, 'asc']],
            "language": languageSettings.en,
        });
    }

});

$(document).ready(function() {
    $('.btn-toggle-analyst-group').on('click', function() {
        var button = $(this);
        var userId = button.data('user-id');
        var isAnalyst = button.data('is-analyst') === 'yes';

        $.ajax({
            url: "/analytics/toggle-analyst-group/", 
            type: "POST",
            data: {
                'user_id': userId,
                'action': isAnalyst ? 'remove' : 'add',
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.status === 'added') {
                    button.text('Remove from Analysts');
                    button.data('is-analyst', 'yes');
                } else if (response.status === 'removed') {
                    button.text('Add to Analysts');
                    button.data('is-analyst', 'no');
                }
            },
            error: function(response) {
                if (response.status === 404) {
                    alert('User not found.');
                } else {
                    alert('An error occurred while updating the analyst group.');
                }
            }
        });
    });
});
