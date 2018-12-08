// DOCUMENT READY
$(document).ready(function() {
    // Collapse and the reopen first news to collapse all the other
    $("div.collapse:not(:first)", "#accordion").removeClass("show");


    // POPOVER for the feed links
    $('[data-toggle="popover"]').popover({'content': getPopoverContent, 'html': true, 'placement': 'bottom', 'trigger': 'manual', 'container': 'body'});

    // This function return the content of the popover
    function getPopoverContent() {
        var content = "";
        content += '<div class="input-group">';
        content += '<input type="text" class="form-control popover-link" readonly value="' + $(this).prop('href') + '" />';
        content += '<div class="input-group-append"><button type="button" class="btn btn-secondary btn-copy">Copia</button></div>';
        content += '</div>';
        content += '<div>' + $(this).data('content') + '</div>';
        return content;
    }

    // Avoid redirection when clicking on the links
    $(".feed-link").on("click", function(e) {
        e.preventDefault();
        return false;
    })

    // Copy the link to clipboard when pressing the button in the popover
    $(document).on ("click", ".btn-copy", function() {
        var link = $(this).parent().parent().children("input")[0].value;
        const el = document.createElement('textarea');
        el.value = link;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
    })

    //Hide popover on next click if outside
    $('body').on('click', function (e) {
        //only buttons
        if ($(e.target).data('toggle') !== 'popover'
            && $(e.target).parents('.popover.show').length === 0) {
            $('[data-toggle="popover"]').popover('hide');
        }
    });

    // Show popover and hide all other if shown
    $('[data-toggle="popover"]').on("click", function() {
        $('[data-toggle=popover]').not('#'+this.id).each(function () {
            $(this).popover('hide');
        });
        $(this).popover('show');
    });

});
