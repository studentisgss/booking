var dataTable;

$(document).ready(function() {
    $("a.btn").on("click", function(e) {
        e.preventDefault();

        var self = this;
        $.get($(this).attr("href"))
            .done(function() {
                $(self).parent().parent().fadeOut(400, function(){
                    $(this).remove();
                    if ($("table").children("tbody").children("tr").length == 0) {
                        $("table").children("tbody").append("<tr><td colspan=\"6\">Nessuna prenotazione in attesa di conferma.</td></tr>");
                    }
                });
            })
            .fail(function() {
                window.location.href = $(self).attr("href");
            });

        return false;
    });

    // Filter and sort the table
    dataTable = $("#table_approvation").DataTable({
        paging: false,
        info: false,
        "columnDefs": [
            { "orderable": false, "targets": 4 },
            { "orderable": false, "targets": 5 },
            { "searchable": false, "targets": 3 },
            { "searchable": false, "targets": 4 },
            { "searchable": false, "targets": 5 },
        ]
    });

    // Show the search input
    $("#filter-form").removeClass("hidden");
    // Remove the DataTable search box
    $("#table_approvation_filter").parent().parent().remove();
    // Add the event handler
    // After the user type something it immediatly filter the table
    $("#search").on("keyup", function(){
        dataTable.search(this.value).draw();
    });
});
