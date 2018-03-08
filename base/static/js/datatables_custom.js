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

/*
Date ordering costumization
*/

var monthDict = {
  "Gennaio" : 1,
  "Febbraio" : 2,
  "Marzo" : 3,
  "Aprile" : 4,
  "Maggio" : 5,
  "Giugno" : 6,
  "Luglio" : 7,
  "Agosto" : 8,
  "Settembre" : 9,
  "Ottobre" : 10,
  "Novembre" : 11,
  "Dicembre" : 12
}

$.fn.dataTable.ext.type.order['formatteddate-pre'] = function ( d ) {
  var spl = d.split("|",3);
  return parseInt(spl[1]);
}
