// DOCUMENT READY
$(document).ready(function() {
    // Collapse and the reopen first news to collapse all the other
    $("div.collapse:not(:first)", "#accordion").removeClass("in");
});
