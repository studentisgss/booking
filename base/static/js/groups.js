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

    // Use AJAX to improve removing single users using the x near the name
    $("a.text-danger").on("click", function(e) {
        // Avoid the dafault behavior
        e.preventDefault();

        // Do the get request asynchronously
        var self = this;
        $.get($(this).attr("href"))
            .done(function() {
                // If all is ok move the option element from the remove select to the add one
                var href = $(self).attr("href");
                var userId = href.substr(href.indexOf("=") + 1);
                var groupId = href.substring(href.lastIndexOf("/") + 1, href.indexOf("?"));
                var option = $("#id_rem-" + groupId + "-members option[value='" + userId + "']");
                var name = $(option).text().toLowerCase();
                var inserted = false;
                // Insert the option in alphabetical order
                $("#id_add-" + groupId + "-members option").each(function() {
                    var opt = $(this).text().toLowerCase();
                    // if name > opt then the option goes after
                    if (opt > name) {
                        $(this).before($(option).clone());
                        inserted = true;
                        return false;
                    }
                });
                // If it wasn't inserted (so last position)
                if (!inserted) {
                    $("#id_add-" + groupId + "-members").append($(option).clone());
                }
                $(option).remove();

                // Reload SumoSelect
                $("#id_rem-" + groupId + "-members")[0].sumo.reload();
                $("#id_add-" + groupId + "-members")[0].sumo.reload();

                // Remove the element
                $(self).parent().fadeOut();
            })
            .fail(function() {
                // If it fails try to go to the page
                window.location.href = $(self).attr("href");
            });

        return false;
    });
});
