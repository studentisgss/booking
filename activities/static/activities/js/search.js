// Variable containing the DataTable
var dataTable;

$(document).ready(function() {
    //Add DataTable
    if ($("#table_events tr")[1].cells.length != 1) {
        if ($("#table_events th").length == 4) {
            dataTable = $("#table_events").DataTable({
                paging: false,
                info: false,
                "columnDefs": [
                    { "searchable": false, "targets": 3 },
                ]
            });
        } else {
            dataTable = $("#table_events").DataTable({
                paging: false,
                info: false,
                "columnDefs": [
                    { "orderable": false, "targets": 4 },
                    { "searchable": false, "targets": 3 },
                    { "searchable": false, "targets": 4 },
                ]
            });
        }
    }
    // Remove the search button
    $("#filter-form div.input-group-btn").remove();
    // Remove the DataTable search box
    $("#table_events_filter").parent().parent().remove();
    // Add the event handler
    // After the user type something it immediatly filter the table
    if (dataTable != null) {
        $("#search").on("keyup", function(){
            dataTable.search(this.value).draw();
        });
    }
});
