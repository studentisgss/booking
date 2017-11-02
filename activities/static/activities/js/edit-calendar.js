var multidatepicker;

$(document).ready(function() {
    // Set multidatepicker, remove date input and show div
    $("#calendar-booking").removeClass("hidden");
    $("#calendar-booking .datetime:even").remove();
    multidatepicker = $("#calendar").multiDatesPicker({dateFormat: "dd/mm/yy"});

    // Fix duplicated ids
    $.each($("#calendar-booking select"), function() { $(this).removeAttr("id"); })
    $.each($("#calendar-booking input"), function() { $(this).removeAttr("id"); })

    $("#add-from-calendar").on('click', function(){
        var vals = multidatepicker.multiDatesPicker('value').replace(" ", "").split(',');
        // If vals consists only of an empty string return
        if (vals[0] == "") {
            return;
        }
        var calendarBooking = $("#calendar-booking");
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
});
