// Variable containing the DataTable
var dataTable;

$(document).ready(function() {
    //Add DataTable
    if ($("#table_events th").length == 4) {
        dataTable = $("#table_events").DataTable({
            paging: true,
            info: false,
            "pageLength": 25,
            "columnDefs": [
                { "searchable": false, "targets": 3 },
            ]
        });
    } else {
        dataTable = $("#table_events").DataTable({
            paging: true,
            info: false,
            "pageLength": 25,
            "columnDefs": [
                { "orderable": false, "targets": 4 },
                { "searchable": false, "targets": 3 },
                { "searchable": false, "targets": 4 },
            ]
        });
    }
    // Remove the search button
    $("#filter-form div.input-group-btn").remove();
    // Add the event handler
    // After the user type something it immediatly filter the table
    $("#search").on("keyup", function(){
        dataTable.search(this.value).draw();
    });
});
