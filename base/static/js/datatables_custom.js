/*
Custom default dataTable value
*/
$.extend( $.fn.dataTable.defaults, {
  /*
  Datatables italian translation
  */
  "language": {
    "paginate": {
        "first":      "Inizio",
        "last":       "Fine",
        "next":       "Successivo",
        "previous":   "Precedente"
    }
  },
  /*
  Dom customization
  */
  "dom": "<'row'<'col-sm-12'tr>><'row'<'col-sm-12'p>>"
} );
