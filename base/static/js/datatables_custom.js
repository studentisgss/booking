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
  var spl = d.split(" ",6);
  if(spl.length !== 5) return 0;
  var startyy = parseInt(spl[1]) % 100;  // max 2 cifre
  var endyy = parseInt(spl[4]) % 100; // max 2 cifre
  var startmth = monthDict[spl[0]]; // max 2 cifre
  var endmth = monthDict[spl[3]]; // max 2 cifre
  var convint = (( endyy*100 + endmth) *100 + startyy ) *100 + startmth; // integer endyy-endmth-startyy-startmth
  return convint;
}
