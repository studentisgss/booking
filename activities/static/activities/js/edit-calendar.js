var multidatepicker;

$(document).ready(function() {
    // Set multidatepicker, remove date input and show div
    $("#calendar-booking").removeClass("hidden");
    $("#calendar-booking .datetime:even").remove();
    var calendarBooking = $("#calendar-booking");
    multidatepicker = $("#calendar").multiDatesPicker({dateFormat: "dd/mm/yy", disabled: true});


    // Fix duplicated ids
    $.each($("#calendar-booking select"), function() { $(this).removeAttr("id"); })
    $.each($("#calendar-booking input"), function() { $(this).removeAttr("id"); })

    // Add event on click
    $("#add-from-calendar").on('click', function(){
        var vals = multidatepicker.multiDatesPicker('value').replace(" ", "").split(',');
        // If vals consists only of an empty string return
        if (vals[0] == "") {
            return;
        }
        $.each(vals, function(i, v){
            event = addForm($('#tr-empty'), true);
            event.removeAttr("id");

            room = $("select[name*='room']", calendarBooking).val();
            $("select[name*='room']", event).val(room);

            status = $("select[name*='status']", calendarBooking).val();
            if (status == 0 && waitingRooms.indexOf(room) > -1) {
                setWaitingWarning(event);
            }
            else {
                $("select[name*='status']", event).val(status);
            }

            $.each($(".datetime:odd", event), function(i, value) {
                $(value).val($(".datetime", calendarBooking)[i].value);
            });
            $.each($(".datetime:even", event), function(i, value) {
                $(value).val(v);
            });
        });
        multidatepicker.multiDatesPicker('resetDates', 'picked')
    });

    // If the user can't approve for this room remove the option and alert
    $("#calendar-booking select[name*='room'].form-control").on("change", function() {
        var div = $(this).parent().parent().parent().parent();
        if (waitingRooms.indexOf(this.value) > -1) {
            setWaitingWarning(div);
        }
        else {
            removeWaitingWarning(div);
        }
    });

    // Disable calendar if anyone of the input is not filled
    calendarBooking.on("change", "select, input", function(){
        var filled = true;
        $.each($("input, select", calendarBooking), function(i, e){
            filled = filled & (this.value != "");
            return filled;
        });
        multidatepicker.multiDatesPicker('disabled', !filled);
        if (filled) {

        } else {
            multidatepicker.multiDatesPicker('resetDates', 'picked')
        }
    });
});
