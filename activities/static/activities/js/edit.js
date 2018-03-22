// Variable for repeat function
var repeatTarget = null;

// HELPER FUNCTION
function setWaitingWarning(tr) {
    tr.addClass("bg-warning");
    tr.attr("title", "Questa prenotazione verrà messa in attesa di approvazione.");
    var select = $("select[name*='status']", tr);
    if (select.val() == 0) {
        select.val(1);
    }
    $("option[value=0]", select).remove();
}

function removeWaitingWarning(tr) {
    tr.removeClass("bg-warning");
    tr.attr("title", "");
    var valOriginal = $("select[name*='status']", tr).val();
    $("select[name*='status']", tr).html(
        $("select[name*='status']", $("#tr-empty")).html()
    );
    $("select[name*='status']", tr).val(valOriginal);
}

function setNoPermissionWarning(tr) {
    tr.addClass("bg-danger");
    tr.attr("title", "Non si possiede nessun permesso su quest'aula. Per poter modificare questa prenotazione si deve selezionare un'altra aula.");
    $("input", tr).prop("readonly", true);
    $("button > span.glyphicon-retweet", tr).parent().prop("disabled", true);
    var status = $("select[name*='status']", tr);
    $("option:not(:selected)", status).each(function() {
        $(this).remove();
    });
}

function removeNoPermissionWarning(tr) {
    tr.removeClass("bg-danger");
    $("input", tr).prop("readonly", false);
    $("button > span.glyphicon-retweet", tr).parent().prop("disabled", false);
    $("option", this).filter(function(i, el){
        return (allRooms.indexOf(el.value) == -1) && (el.value != "");
    }).remove();
    var valOriginal = $("select[name*='status']", tr).val();
    $("select[name*='status']", tr).html(
        $("select[name*='status']", $("#tr-empty")).html()
    );
    $("select[name*='status']", tr).val(valOriginal);
}

function addForm(element, before = false) {
    var id = $("#id_event_set-TOTAL_FORMS").val();
    $("#id_event_set-TOTAL_FORMS").val(parseInt(id) + 1);
    var el = $($(element)[0].outerHTML.replace(/__prefix__/g, id));
    el.removeAttr("id");
    if (before) {
        // Find the last filled form
        var elementAfter = $("#table-events tr").filter(function() {
            var tr = $(this);
            var filled = false;
            $("select[name*='room']", tr).each(function() {
                filled |= $(this).val() != "";
            });
            if (filled) { // If the form is already filled do not go further
                return filled;
            }
            $("input[type='text']", tr).each(function() {
                filled |= $(this).val() != "";
            });
            return filled;
        }).last();
        el.insertAfter(elementAfter);
    }
    else {
        el.insertBefore($('#tr-button'));
    }
    el.removeClass("hidden");
    $(".datetime:even", el).removeClass("hasDatepicker");
    $(".datetime:even", el).datepicker();
    return el;
}

function clearModal() {
    var modal = $("#repeat-modal");
    $("input:not([type=\"checkbox\"])", modal).val("");
    $("input[type=\"checkbox\"]", modal).prop("checked", false);
}

function checkInput(obj) {
    var tr = $(obj).parent().parent();
    if ($(obj).hasClass("hasDatepicker")) {
        $(obj).trigger("change");
    }
    var select = $("select[name*='status']", tr);
    var roomVal = $("select[name*='room']", tr).val();
    if (($("select[name*='room']", tr).data("original-value") != roomVal) ||
            ($("select[name*='status']", tr).data("original-value") != 0)) {
        return;
    }
    var inputs = $("input", tr);
    var originalValue = true;
    inputs.each(function() {
        originalValue = originalValue && ($(this).data("original-value") == this.value);
    });
    if (originalValue) {
        removeWaitingWarning(tr);
        $("select[name*='status']", tr).val(0);
    }
    else {
        setWaitingWarning(tr);
    }
}

// DOCUMENT READY
$(document).ready(function() {
    // Highlight event which cannot be approved
    $(document).on("change", "select[name*='room'].form-control", function() {
        var tr = $(this).parent().parent();
        if (waitingRooms.indexOf(this.value) > -1) {
            setWaitingWarning(tr);
            if ($(this).data("original-value")) {
                checkInput(this);
            }
        }
        else {
            if ((allRooms.indexOf(this.value) == -1) && (this.value != "")) {
                setNoPermissionWarning(tr);
            } else {
                removeWaitingWarning(tr);
            }
        }
    });

    // Enhanced select control with jquery sumoselect

    $("#id_managers").SumoSelect({
    	placeholder: 'Selezionare i referenti',
        captionFormat:'{0} selezionati',
        captionFormatAllSelected:'{0} tutti selezionati',
        search: true,
        searchText: 'Cerca...',
        noMatch: 'Nessuna corrispondenza per "{0}"',
        locale: ['OK', 'Annulla', 'Seleziona tutti']
	});

    // Enhance delete
    var span = $("span.glyphicon-trash");
    span.parent().removeClass("hidden");
    span.parent().siblings("input").addClass("hidden");

    $(document).on("click", "button.remover", function() {
        if ($(this).siblings("input").prop("checked")) {
            $(this).siblings("input").prop("checked", false);
            var removeTr = $(this).parent().parent();
            $("input", removeTr).each(function(i){
                $(this).prop("readonly", $(this).data("previous-state"));
            });
            $("button > span.glyphicon-retweet", removeTr).parent().prop("disabled", $("button > span.glyphicon-retweet", removeTr).parent().data("previous-state"));
            $("td:not(:nth-last-child(3))", removeTr).css("opacity", 1);
            // Check if the previous tr is an error
            if ($(removeTr).prev().children().length == 1) {
                $(removeTr).prev().css("opacity", 1);
            }
            //Chage the button
            $(this).html("<span class=\"glyphicon glyphicon-trash\" aria-hidden=\"true\"></span>");
            $(this).removeClass("btn-info");
            $(this).addClass("btn-danger");
        } else {
            $(this).siblings("input").prop("checked", true);
            var removeTr = $(this).parent().parent();
            $("input", removeTr).each(function(i){
                $(this).data("previous-state", $(this).prop("readonly"));
                $(this).prop("readonly", true);
            });
            $("button > span.glyphicon-retweet", removeTr).parent().data("previous-state", $("button > span.glyphicon-retweet", removeTr).parent().prop("disabled"));
            $("button > span.glyphicon-retweet", removeTr).parent().prop("disabled", true);
            $("td:not(:nth-last-child(3))", removeTr).css("opacity", 0.3);
            // Check if the previous tr is an error
            if ($(removeTr).prev().children().length == 1) {
                $(removeTr).prev().css("opacity", 0.3);
            }
            //Chage the button
            $(this).html("<span class=\"glyphicon glyphicon-repeat\" aria-hidden=\"true\"></span>");
            $(this).removeClass("btn-danger");
            $(this).addClass("btn-info");
        }
    });

    // Set the dates of start and end automatically
    $(document).on("change", ".datetime:even", function() {
        tr = $(this).parent().parent();
        $(".datetime:even", tr).val($(this).val());
    });

    // Add button
    $("#tr-button").removeClass("hidden");
    $("#add-button").on("click", function() {
        addForm($('#tr-empty'));
    });

    //REPEAT FUNCTION
    $("button[data-target=\"#repeat-modal\"]").removeClass("hidden");
    $("th").removeClass("hidden");

    $("#repeat-modal").on("show.bs.modal", function(e) {
        clearModal();
        var btn = $(e.relatedTarget);
        var tr = btn.parent().parent();
        repeatTarget = tr;
        var date = $(".datetime:first", tr).val();
        if (date) {
            dateSplit = date.split("/");
            var d = new Date(dateSplit[2], dateSplit[1] - 1, dateSplit[0]);
            d.setDate(d.getDate() + 1);
            $("#date-from", $(this)).val(d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear());
        }
    });

    $("#btn-repeat").on("click", function() {
        var modal = $("#repeat-modal");
        var days = $("input[name='day']:checked", modal).map(function(index,domElement) {
            return parseInt($(domElement).val());
        }).get();
        days.sort();
        var startDate = $("#date-from", modal).val();
        var times = $("#repeat-times", modal).val();
        if (!(days.length > 0 && startDate && times)) {
            $("#repeat-form", modal).addClass("has-error");
            return;
        }

        var dateSplit = startDate.split("/");
        var date = new Date(dateSplit[2], dateSplit[1] - 1, dateSplit[0]);

        // Get the first day greater or equal than date in days
        while (days.indexOf(date.getDay()) == -1) {
            date.setDate(date.getDate() + 1);
        }

        var event = null;
        var room = null;
        var status = null;
        while (times > 0) {
            // Add the new event
            event = addForm($('#tr-empty'), true);
            event.removeAttr("id");
            room = $("select[name*='room']", repeatTarget).val();
            $("select[name*='room']", event).val(room);
            status = $("select[name*='status']", repeatTarget).val();
            if (status == 0 && waitingRooms.indexOf(room) > -1) {
                setWaitingWarning(event);
            }
            else {
                $("select[name*='status']", event).val(status);
            }

            $.each($(".datetime:odd", event), function(i, value) {
                $(value).val($(".datetime:odd", repeatTarget)[i].value);
            });
            $.each($(".datetime:even", event), function(i, value) {
                $(value).val(date.getDate() + "/" + (date.getMonth() + 1) + "/" + date.getFullYear());
            });

            // Find next date and decrement times
            times -= 1;
            var oldDay = date.getDay();
            var index = (days.indexOf(oldDay) + 1) % days.length;
            var daysDiff = days[index] - oldDay;
            if (daysDiff <= 0) {
                daysDiff += 7;
            }
            date.setDate(date.getDate() + daysDiff);
        }
        $("#repeat-modal").modal("hide");
    });

    // Room without any permission and set initial status
    $("select[name*='room'].form-control").each(function() {
        if ((allRooms.indexOf(this.value) == -1) && (this.value != "")) {
            var tr = $(this).parent().parent();
            setNoPermissionWarning(tr);
            $(this).on("change", function() {
                var tr = $(this).parent().parent();
                removeNoPermissionWarning(tr);
            });
        }
        if ((this.value != "") && (waitingRooms.indexOf(this.value) > -1)) {
            var tr = $(this).parent().parent();
            var select = $("select[name*='status']", tr);
            if (select.val() != 0) {
                $("option[value=0]", select).remove();
            }
            if (select.val() == 1) {
                setWaitingWarning(tr);
            }
            $("input", tr).each(function() {
                $(this).data("original-value", this.value);
            });
            $("select", tr).each(function() {
                $(this).data("original-value", this.value);
            });
            $("input:not(.hasDatepicker)", tr).on("change", function(){ checkInput(this); });
            $("input.hasDatepicker", tr).datepicker("option", "onSelect", function(){ checkInput(this); });
        }
    });
});
