// Variable containing the DataTable
var dataTable;

$(document).ready(function() {
    //Add DataTable
  if ($("#table_events tr")[1].cells.length != 1) {
      if ($("#table_events th").length == 4) {
          dataTable = $("#table_events").DataTable({
              paging: ($("#table_events tr").length > 25),
              info: false,
              "pageLength": 25,
              "columnDefs": [
                  { "searchable": false, "targets": 3 },
                  { "type" : "formatteddate", "targets" : 3}
              ]
          });
      } else {
          dataTable = $("#table_events").DataTable({
              paging: ($("#table_events tr").length > 25),
              info: false,
              "pageLength": 25,
              "columnDefs": [
                  { "orderable": false, "targets": 4 },
                  { "searchable": false, "targets": 3 },
                  { "searchable": false, "targets": 4 },
                  { "type" : "formatteddate", "targets" : 3}
              ]
          });
      }
    }
    // Remove the search button
    $("#filter-form div.input-group-btn").remove();
    // Prevent html+javascript double search making a do-nothing form
    $("#filter-form").attr("action","javascript:return false;");
    // Add the event handler
    // After the user type something it immediatly filter the table
    if (dataTable != null) {
        $("#search").on("keyup", function(){
            dataTable.search(this.value).draw();
        });
    }
});
