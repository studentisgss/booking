var dataTable;

$(document).ready(function() {
    $("a.btn:not(.filter)").on("click", function(e) {
        // Avoid the dafault behavior
        e.preventDefault();

        // Do the get request asynchronously
        var self = this;
        $.get($(this).attr("href"))
            .done(function() {
                // If all is ok remove the tr
                $(self).parent().parent().fadeOut(400, function(){
                    $(this).remove();
                    // If the table is empty
                    if ($("table").children("tbody").children("tr").length == 0) {
                        $("table").children("tbody").append("<tr><td colspan=\"6\">Nessuna prenotazione in attesa di conferma.</td></tr>");
                    }
                });
            })
            .fail(function() {
                // If it fails try to go to the page
                window.location.href = $(self).attr("href");
            });

        return false;
    });
    // if the table is not empty
    if ($("#table_approvation tr")[1].cells.length != 1) {
      // Filter and sort the table
      dataTable = $("#table_approvation").DataTable({
          paging: false,
          info: false,
          "bAutoWidth": false,
          // Dafault: do not change the order
          "order": [],
          "columnDefs": [
              { "orderable": false, "targets": 4 },
              { "orderable": false, "targets": 5 },
              { "searchable": false, "targets": 3 },
              { "searchable": false, "targets": 4 },
              { "searchable": false, "targets": 5 },
          ]
      });
    }

    // Show the search input
    $("#filter").removeClass("hidden");
    // Remove the DataTable search box
    $("#table_approvation_filter").parent().parent().remove();
    // Add the event handler
    // After the user type something it immediatly filter the table if it is not null
    if (dataTable != null) {
      $("#search").on("keyup", function(){
          dataTable.search(this.value).draw();
      });
    }
});
