document.addEventListener('DOMContentLoaded', (event) => {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            trigger: 'click'
        });
    });

    popoverTriggerList.forEach(function (popoverTriggerEl) {
        popoverTriggerEl.addEventListener('click', function (e) {
            // Close all popovers except the one being clicked
            popoverTriggerList.forEach(function (el) {
                if (el !== popoverTriggerEl) {
                    let popoverInstance = bootstrap.Popover.getInstance(el);
                    if (popoverInstance) {
                        popoverInstance.hide();
                    }
                }
            });
            // Allow the clicked popover to toggle
            e.stopPropagation();
        });
    });

    document.body.addEventListener('click', function (e) {
        // Close all popovers when clicking outside
        popoverTriggerList.forEach(function (popoverTriggerEl) {
            let popoverInstance = bootstrap.Popover.getInstance(popoverTriggerEl);
            if (popoverInstance && !popoverTriggerEl.contains(e.target)) {
                popoverInstance.hide();
            }
        });
    });
});
