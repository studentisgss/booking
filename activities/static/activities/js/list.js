$(document).ready(function() {
    dataTable = $("#table_events").DataTable({
        searching: false,
        paging: false,
        info: false,
        "columnDefs": [
            { "orderable": false, "targets": 4 },
        ]
    });
});
