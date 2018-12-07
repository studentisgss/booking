$(document).ready(function() {
    // Enhance delete
    // if js is enabled substitute the button
    var span = $("span.fa-trash-alt");
    span.parent().removeClass("d-none");
    span.parent().siblings("input").addClass("d-none");
    // when the button is clicked then
    // - check the form
    // - hide the row of the table
    $(document).on("click", "button.remover", function() {
        if ($(this).siblings("input").prop("checked")) {
            $(this).siblings("input").prop("checked", false);
            var removeTr = $(this).parent().parent();
            $("input", removeTr).each(function(i){
                $(this).prop("readonly", false);
            });
            $("td:not(:nth-last-child(2))", removeTr).css("opacity", 1);
            //Chage the button
            $(this).html("<span class=\"fas fa-trash-alt\" aria-hidden=\"true\"></span>");
            $(this).removeClass("btn-info");
            $(this).addClass("btn-danger");
        } else {
            $(this).siblings("input").prop("checked", true);
            var removeTr = $(this).parent().parent();
            $("input", removeTr).each(function(i){
                $(this).prop("readonly", true);
            });
            $("td:not(:nth-last-child(2))", removeTr).css("opacity", 0.3);
            //Chage the button
            $(this).html("<span class=\"fas fa-undo\" aria-hidden=\"true\"></span>");
            $(this).removeClass("btn-danger");
            $(this).addClass("btn-info");
        }
    });
})
