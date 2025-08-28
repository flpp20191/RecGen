// delete cookie
function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/';
}

// Set  cookie
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}


document.addEventListener('DOMContentLoaded', function () {
    const jsData = document.getElementById('js-data');
    const csrfToken = jsData.dataset.csrfToken;
    const updateTrackingStatusUrl = jsData.dataset.updateTrackingUrl;

    update_tracking_status(csrfToken, updateTrackingStatusUrl);
});

function update_tracking_status(csrfToken, updateTrackingStatusUrl){
    $('.tracking-checkbox').change(function() {
        let categoryId = $(this).val();
        let isTracking = $(this).is(':checked');
        $.ajax({
            url: "update_tracking_status/",
            data: {
                'category_id': categoryId,
                'is_tracking': isTracking,
                'csrfmiddlewaretoken': csrfToken,
            },
            dataType: 'json',
            method: 'POST',
            success: function (data) {
                if (data.status !== 'ok') {
                    alert('An error occurred.');
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('An error occurred: ' + jqXHR);
            }
        });
    });
}

function defaultCheckeMentor(csrfToken, updateEMentorTrackingStatusUrl){
    $('#defaultCheckeMentor').change(function() {
        var isChecked = $(this).is(":checked");
        console.log("defaultCheckeMentor function is now loaded and ready to use.");
        $.ajax({
            url: "update_ementor_tracking_status/",
            method: 'POST',
            data: {
                'is_tracking_eMentor': isChecked,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                // Handle success
            },
            error: function(error) {
                console.error("Error updating tracking status:", error);
            }
        });
    });
}
