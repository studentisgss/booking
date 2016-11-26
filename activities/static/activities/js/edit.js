$(document).ready(function() {
	// Highlight event which cannot be approved
	$("select.form-control").on("change", function(){
		var tr = $(this).parent().parent()
		if (waitingRooms.indexOf(this.value) > -1)
		{
			tr.addClass("warning");
			tr.attr("title", "Questa prenotazione verrà messa in attesa di approvazione.");
		}
		else
		{
			tr.removeClass("warning");
			tr.attr("title", "");
		}
	});

	// Enhance delete
	var span = $("span.glyphicon-trash");
	span.removeClass("hidden");
	span.parent().siblings("input").addClass("hidden");
	$(document).on("click", "a.remover", function(){
		$(this).siblings("input").prop("checked", true);
		$(this).parent().parent().fadeOut();
	});

	// Set the dates of start and end automatically
	$(document).on("change", ".datetime:even", function(){
		tr = $(this).parent().parent();
		$(".datetime:even", tr).val($(this).val());
	});

	// Add button
	$("#add-button").on("click", function(){
		var id = $("#id_event_set-TOTAL_FORMS").val();
		$("#id_event_set-TOTAL_FORMS").val(id + 1);
		var el = $($('#tr-empty')[0].outerHTML.replace(/__prefix__/g, id));
		el.insertBefore($('#tr-button'));
		el.removeClass("hidden");
		$(".datetime:even", el).removeClass("hasDatepicker")
		$(".datetime:even", el).datepicker();
	});
});