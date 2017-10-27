// DOCUMENT READY
$(document).ready(function() {
    descriptionShown = false;
    $("#collapseDescriptionControl").on("click", function() {
        descriptionShown = !descriptionShown;
        if (descriptionShown) {
            $("#collapseDescriptionControl").html("<span class=\"glyphicon glyphicon-chevron-up\"></span> Nascondi descrizione <span class=\"glyphicon glyphicon-chevron-up\"></span>");
        } else {
            $("#collapseDescriptionControl").html("<span class=\"glyphicon glyphicon-chevron-down\"></span> Mostra descrizione <span class=\"glyphicon glyphicon-chevron-down\"></span>");
        }
    });
    $("#collapseDescriptionControl").html("<span class=\"glyphicon glyphicon-chevron-down\"></span> Mostra descrizione <span class=\"glyphicon glyphicon-chevron-down\"></span>");
});
