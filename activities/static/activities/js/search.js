// Variable containing the DataTable
var dataTable;

$(document).ready(function() {
    //Add DataTable
    dataTable = $("#table_events").DataTable({
        paging: false,
        info: false,
        "columnDefs": [
            { "orderable": false, "targets": 4 },
            { "searchable": false, "targets": 3 },
            { "searchable": false, "targets": 4 },
        ]
    });
    // Remove the search button
    $("#filter-form div.input-group-btn").remove();
    // Remove the DataTable search box
    $("#table_events_filter").parent().parent().remove();
    // Add the event handler
    // After the user type something it immediatly filter the table
    $("#search").on("keyup", function(){
        dataTable.search(this.value).draw();
    });
});
