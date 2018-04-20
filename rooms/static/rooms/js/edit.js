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
        $(this).siblings("input").prop("checked", true);
        $(this).parent().parent().parent().fadeOut();
    });
})
