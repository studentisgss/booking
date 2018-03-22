$(document).ready(function(){
    // Enhanced select control with jquery sumoselect

    $("#id_managers").SumoSelect({
    	placeholder: 'Selezionare i referenti',
        captionFormat:'{0} selezionati',
        captionFormatAllSelected:'{0} tutti selezionati',
        search: true,
        searchText: 'Cerca...',
        noMatch: 'Nessuna corrispondenza per "{0}"',
        locale: ['OK', 'Annulla', 'Seleziona tutti']
	});
});
