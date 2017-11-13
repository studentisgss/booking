$(document).ready(function() {
    if ($("#table_events th").length == 4) {
        dataTable = $("#table_events").DataTable({
            searching: false,
            paging: false,
            info: false
        });
    } else {
        dataTable = $("#table_events").DataTable({
            searching: false,
            paging: false,
            info: false,
            "columnDefs": [
                { "orderable": false, "targets": 4 },
            ]
        });
    }
});
