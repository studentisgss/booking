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
});
