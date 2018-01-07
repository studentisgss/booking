// A matrix containing the DataTables and the name, one for every building
var dataTables = [];

$(document).ready(function() {
    // Add DataTable
    // remove the possibility to order the column with edit buttons
    if ($('.table').find('tr')[0].cells.length == 3) {
      $('table').each(function(i, obj) {
        // inizialize the matrix
        dataTables[i] = [];
        dataTables[i][1] = $(this).DataTable({
          paging: false,
          info: false,
          //searching: false,
          "columnDefs": [
              { "orderable": false, "targets": 1 },
              { "searchable": false, "targets": 2 },
              { "orderable": false, "targets": 2 },
            ]
        })
      });
    } else {
      $('table').each(function(i, obj) {
        // inizialize the matrix
        dataTables[i] = [];
        dataTables[i][1] = $(this).DataTable({
          paging: false,
          info: false,
          //searching: false,
          "columnDefs": [
              { "orderable": false, "targets": 1 },
            ]
          })
      });
    };
    // hide the search input on every table
    $('.dataTables_filter').addClass("hidden");
    // add name of the building
    $('.building_name').each(function(i, obj) {
      dataTables[i][0] = $(this).text();
    });

    $('#search').keyup(function() {
      var text = this.value.toLowerCase();
      for (i = 0; i < dataTables.length; i++) {
        dataTables[i][1].search("").draw();
        // if the text match with the name of the building dont't filter the rooms
        if (dataTables[i][0].toLowerCase().search(text) == -1) {
          dataTables[i][1].search(text).draw();
        }
      }
    });
});
