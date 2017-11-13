var multidatepicker;
var activeDate = new Date(Date.now());
activeDate.setDate(1);
var checkedDate; // Months for which the disabled day have already been retrived
var cachedTooltips = {}; // Cached tooltips
var activeTimeouts = []; // List of active timeouts

// If the string has only 1 character add a leading zero
function strPadding(obj) {
    var s = String(obj);
    if (s.length < 2) {
        s = "0" + s;
    }
    return s;
}

$(document).ready(function() {
    // Set multidatepicker, remove date input and show div
    $("#calendar-booking").removeClass("hidden");
    $("#calendar-booking .datetime:even").remove();
    var calendarBooking = $("#calendar-booking");
    // onChangeMonthYear: when changing month retrieve the disabled day for the next/previous month
    multidatepicker = $("#calendar").multiDatesPicker({dateFormat: "dd/mm/yy", disabled: true, onChangeMonthYear: function(y, m,inst){
        if (multidatepicker.multiDatesPicker('disabled') == false) {
            // Set from and to to the first day of the current month
            var fromDate = new Date(y, m - 1, 1);
            var toDate = new Date(y, m - 1, 1);
            if (fromDate > activeDate) { // If going next month
                fromDate.setMonth(fromDate.getMonth() + 1);
                toDate.setMonth(toDate.getMonth() + 2);
                toDate.setDate(0);
            } else { // If going to the previous month
                fromDate.setMonth(fromDate.getMonth() - 1);
                toDate.setDate(0);
            }
            if (checkedDate.indexOf(fromDate.getTime()) == -1) { // If not already retrieved, get the days
                $.get("/activities/bookeddates", {room: $("#calendar-booking select[name*='room']").val(),
                                                 start: $("#calendar-booking input[name*='start']").val(),
                                                 end: $("#calendar-booking input[name*='end']").val(),
                                                 from: strPadding(fromDate.getDate()) + "/" + strPadding(fromDate.getMonth() + 1) + "/" + String(fromDate.getFullYear()),
                                                 to: strPadding(toDate.getDate()) + "/" + strPadding(toDate.getMonth() + 1) + "/" + String(toDate.getFullYear())})
                .done(function(data){
                    if (data.length > 0) {
                        multidatepicker.multiDatesPicker('addDates', data, 'disabled');
                    }
                    checkedDate.push(fromDate.getTime()) // Add the retrieved month to the saved ones.
                });
            }
        }
        activeDate = new Date(y, m - 1, 1);
    }, beforeShowDay: function(d) {
        return [true, "cust-tooltip", ""];
    }});


    // Fix duplicated ids
    $.each($("#calendar-booking select"), function() { $(this).removeAttr("id"); })
    $.each($("#calendar-booking input"), function() { $(this).removeAttr("id"); })

    // Add events on click on "add" button
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
        // Room change: clear cached tooltips
        cachedTooltips = {};
    });

    // Disable calendar if anyone of the input is not filled
    calendarBooking.on("change", "select, input", function(){
        var filled = true;
        $.each($("input, select", calendarBooking), function(i, e){
            filled = filled && (this.value != "");
            return filled;
        });
        multidatepicker.multiDatesPicker('disabled', !filled);
        multidatepicker.multiDatesPicker('resetDates', 'disabled');

        if (filled) { // If calendar is active then get the disabled days for the current, the previous and the next month
            var fromDate = new Date(Date.now());
            fromDate.setDate(1);
            fromDate.setMonth(fromDate.getMonth()-1);
            var toDate = new Date(Date.now());
            toDate.setMonth(toDate.getMonth()+2);
            toDate.setDate(0);

            $.get("/activities/bookeddates", {room: $("#calendar-booking select[name*='room']").val(),
                                             start: $("#calendar-booking input[name*='start']").val(),
                                             end: $("#calendar-booking input[name*='end']").val(),
                                             from: strPadding(fromDate.getDate()) + "/" + strPadding(fromDate.getMonth() + 1) + "/" + String(fromDate.getFullYear()),
                                             to: strPadding(toDate.getDate()) + "/" + strPadding(toDate.getMonth() + 1) + "/" + String(toDate.getFullYear())})
            .done(function(data){
                if (data.length > 0) {
                    multidatepicker.multiDatesPicker('addDates', data, 'disabled');
                    var now = new Date(Date.now());
                    now.setDate(1);
                    now.setHours(0);
                    now.setMinutes(0);
                    now.setSeconds(0);
                    now.setMilliseconds(0);
                    fromDate.setHours(0);
                    fromDate.setMinutes(0);
                    fromDate.setSeconds(0);
                    fromDate.setMilliseconds(0);
                    toDate.setDate(1);
                    toDate.setHours(0);
                    toDate.setMinutes(0);
                    toDate.setSeconds(0);
                    toDate.setMilliseconds(0);
                    // Add the months to the saved ones. Use getTime() to avoid javascript issue.
                    checkedDate = [fromDate.getTime(), toDate.getTime(), now.getTime()];
                }
            });
        } else {
            // If the calendar is disabled reset the dates.
            multidatepicker.multiDatesPicker('resetDates', 'picked');
        }
    });

    $("#calendar-booking").on("mouseenter", "#calendar td > span:first-child, #calendar td > a", function(){
        var createTooltip = function(el){
            var day = 1;
            var index = $(el).html().indexOf("<");
            if (index == -1) {
                day = $(el).html();
            } else {
                day = $(el).html().substring(0, index).trim();
            }
            var month = activeDate.getMonth()+1;
            var year = activeDate.getFullYear();
            var date = strPadding(day) + "/" + strPadding(month) + "/" + String(year);
            if (date in cachedTooltips) {
                // $(el).attr("title", cachedTooltips[date]); OLD VERSION
                if ($(el).siblings("span.cust-tooltiptext").length == 0) { // If the tooltip is not already set
                    // $(el).parent().addClass("cust-tooltip");
                    $(el).after("<span class=\"cust-tooltiptext ui-datepicker-unselectable\">" + cachedTooltips[date] + "</span>");
                }
            } else {
                $.get("/activities/bookedhours", {room: $("#calendar-booking select[name*='room']").val(),
                                                 day: date}).done(function(data){
                                                    var title = "";
                                                    if (data["booked"].length == 0){
                                                        if (data["opening"] != ""){
                                                            title = "Orario apertura:\n" + data["opening"];
                                                        } else {
                                                            title = "Nessuna prenotazione.";
                                                        }
                                                    } else {
                                                        title = "Aula prenotata:\n"
                                                        title += data["booked"].join("\n");
                                                        if (data["opening"] != ""){
                                                            title += "\n\nOrario apertura:\n" + data["opening"];
                                                        }
                                                    }
                                                    // $(el).parent().addClass("cust-tooltip");
                                                    $(el).after("<span class=\"cust-tooltiptext ui-datepicker-unselectable\">" + title + "</span>");
                                                    //$(el).html($(el).html() + "<span class=\"cust-tooltiptext ui-datepicker-unselectable\">" + title + "</span>");
                                                    cachedTooltips[date] = title;
                                                 });
            }
        };
        if (multidatepicker.multiDatesPicker('disabled') == false) {
            var t = setTimeout(createTooltip, 1000, this);
            activeTimeouts.push(t);
        }
    });

    $("#calendar-booking").on("mouseleave", "#calendar td span, #calendar td a", function(){
        $.each(activeTimeouts, function(i, t){
            clearTimeout(t);
        });
    });
});
