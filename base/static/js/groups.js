$(document).ready(function() {
    $("select").SumoSelect({
    	placeholder: 'Selezionare gli utenti',
        captionFormat:'{0} selezionati',
        captionFormatAllSelected:'{0} tutti selezionati',
        selectAll: true,
        search: true,
        searchText: 'Cerca...',
        noMatch: 'Nessuna corrispondenza per "{0}"',
        locale: ['OK', 'Annulla', 'Seleziona tutti']
	});
});
