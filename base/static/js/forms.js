$(document).ready(function() {
    $(".date").datepicker();
    $(".date").attr("placeholder", "gg/mm/aaaa");
    // A datetime field has two input: the first is a date, the second is a time
    $(".datetime:even").datepicker();
    $(".datetime:even").attr("placeholder", "gg/mm/aaaa");
    $(".datetime:odd").attr("placeholder", "hh:mm:ss");
});