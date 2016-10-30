$(document).ready(function() {
    $(".date").datepicker();
    // A datetime field has two input: the first is a date, the second is a time
    $(".datetime:even").datepicker();
    $(".datetime:odd").attr("placeholder", "hh:mm:ss")
});