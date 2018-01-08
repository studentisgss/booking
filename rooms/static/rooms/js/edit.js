$(document).ready(function() {
    // Enhance delete
    // if js is enabled substitute the button
    var span = $("span.glyphicon-trash");
    span.parent().removeClass("hidden");
    span.parent().siblings("input").addClass("hidden");
    // when the button is clicked then
    // - check the form
    // - hide the row of the table
    $(document).on("click", "button.remover", function() {
        $(this).siblings("input").prop("checked", true);
        $(this).parent().parent().parent().fadeOut();
    });
})
