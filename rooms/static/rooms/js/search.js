// A matrix containing the DataTables, the name and the div in the template, one for every building
var dataTables = [];

$(document).ready(function() {
    // Remove the search button
    $("#filter-form div.input-group-btn").remove();
    // this flag is true only if there the column with the edit buttons in the tables
    edit_column = $(".table").find('tr')[0].cells.length == 3;
    $('.building_div').each(function(i, obj) {
      dataTables[i] = [];
      // Add building name
      dataTables[i][0] = $(this).find(".building_name").text();
      // Add DataTable
      try {
        // remove the possibility to order the column with edit buttons
        if (edit_column) {
          dataTables[i][1] = $(this).find(".building_table").DataTable({
            paging: false,
            info: false,
            "language": {
              "emptyTable": "Nessuna aula corrispondente trovata."
            },
            "columnDefs": [
                { "orderable": false, "targets": 1 },
                { "searchable": false, "targets": 2 },
                { "orderable": false, "targets": 2 },
              ]
          })
        } else {
          dataTables[i][1] = $(this).find(".building_table").DataTable({
            paging: false,
            info: false,
            "language": {
              "emptyTable": "Nessuna aula corrispondente trovata."
            },
            "columnDefs": [
                { "orderable": false, "targets": 1 },
              ]
          });
        }
      }
      catch(err) {
        dataTables[i][1] = null; // the table is empty
      }
      // add div
      dataTables[i][2] = $(this);
    });

    // hide the search input on every table
    $('.dataTables_filter').addClass("hidden");
    // search: filter by room or building
    $('#search').keyup(function() {
      // searched text
      var text = this.value.toLowerCase();
      // track if all te buldings divs are hidden
      var no_buildings_shown = true;
      for (i = 0; i < dataTables.length; i++) {
        // filter the rooms in the table
        if (dataTables[i][1] != null) {
          dataTables[i][1].search("").draw();
          // if the text match with the name of the building dont't filter the rooms
          if (dataTables[i][0].toLowerCase().search(text) == -1) {
            dataTables[i][1].search(text).draw();
          }
        }
        dataTables[i][2].removeClass("hidden");
        // hide all if there are no rooms matched rooms
        if (dataTables[i][2].find("tr")[1].cells.length == 1) {
          dataTables[i][2].addClass("hidden");
        } else {
          no_buildings_shown = false;
        }
      }
      if (no_buildings_shown) {
        $("#no_rooms_search").removeClass("hidden");
        $("#no_rooms_search_text").html(text);
      } else {
        $("#no_rooms_search").addClass("hidden");
      }
    });
});
