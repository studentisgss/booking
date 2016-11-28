// Variable for repeat function
var repeatTarget = null;

$(document).ready(function() {
	// Highlight event which cannot be approved
	$("select.form-control").on("change", function(){
		var tr = $(this).parent().parent();
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
	span.parent().removeClass("hidden");
	span.parent().siblings("input").addClass("hidden");
	$(document).on("click", "button.remover", function(){
		$(this).siblings("input").prop("checked", true);
		$(this).parent().parent().fadeOut();
	});

	// Set the dates of start and end automatically
	$(document).on("change", ".datetime:even", function(){
		tr = $(this).parent().parent();
		$(".datetime:even", tr).val($(this).val());
	});

	function AddForm(element) {
		var id = $("#id_event_set-TOTAL_FORMS").val();
		$("#id_event_set-TOTAL_FORMS").val(parseInt(id) + 1);
		var el = $($(element)[0].outerHTML.replace(/__prefix__/g, id));
		el.removeAttr("id");
		el.insertBefore($('#tr-button'));
		el.removeClass("hidden");
		$(".datetime:even", el).removeClass("hasDatepicker")
		$(".datetime:even", el).datepicker();
		return el;
	}

	// Add button
	$("#tr-button").removeClass("hidden");
	$("#add-button").on("click", function(){
		AddForm($('#tr-empty'));
	});

	//REPEAT FUNCTION
	$("button[data-target=\"#repeat-modal\"]").removeClass("hidden");
	$("th").removeClass("hidden");

	function clearModal(){
		var modal = $("#repeat-modal");
		$("input:not([type=\"checkbox\"])", modal).val("");
		$("input[type=\"checkbox\"]", modal).prop("checked", false);
	}

	$("#repeat-modal").on("show.bs.modal", function(e){
		clearModal();
		var btn = $(e.relatedTarget);
		var tr = btn.parent().parent();
		repeatTarget = tr;
		var date = $(".datetime:first", tr).val();
		if (date){
			dateSplit = date.split("/");
			var d = new Date(dateSplit[2], dateSplit[1] - 1, dateSplit[0]);
			d.setDate(d.getDate() + 1);
			$("#date-from", $(this)).val(d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear());
		}
	});

	$("#btn-repeat").on("click", function(){
		var modal = $("#repeat-modal");
		var days = $("input[name='day']:checked", modal).map(function(index,domElement) {
		    return parseInt($(domElement).val());
		}).get();
		days.sort();
		var startDate = $("#date-from", modal).val();
		var times = $("#repeat-times", modal).val();
		if (!(days.length > 0 && startDate && times)){
			$("#repeat-form", modal).addClass("has-error");
			return;
		}

		var dateSplit = startDate.split("/");
		var date = new Date(dateSplit[2], dateSplit[1] - 1, dateSplit[0]);

		// Get the first day greater or equal than date in days
		while (days.indexOf(date.getDay()) == -1) {
			date.setDate(date.getDate() + 1);
		}

		while (times > 0) {
			// Add the new event
			var event = AddForm($('#tr-empty'))
			event.removeAttr("id");
			$("select", event).val($("select", repeatTarget).val());
			$.each($(".datetime:odd", event), function(i, value){
				$(value).val($(".datetime:odd", repeatTarget)[i].value);
			});
			$.each($(".datetime:even", event), function(i, value){
				$(value).val(date.getDate() + "/" + (date.getMonth() + 1) + "/" + date.getFullYear());
			});

			// Find next date and decrement times
			times -= 1;
			var oldDay = date.getDay();
			var index = (days.indexOf(oldDay) + 1) % days.length;
			var daysDiff = days[index] - oldDay;
			if (daysDiff <= 0)
				daysDiff += 7;
			date.setDate(date.getDate() + daysDiff);
		}
		$("#repeat-modal").modal("hide");
	});


	// Room without any permission
	$("select.form-control").each(function(){
		if ((allRooms.indexOf(this.value) == -1) && (this.value != ""))
		{
			var tr = $(this).parent().parent();
			tr.addClass("danger");
			tr.attr("title", "Non si possiede nessun permesso su quest'aula. Per poter modificare questa prenotazione si deve selezionare un'altra aula.");
			$("input", tr).prop("disabled", true);
			$("button > span.glyphicon-retweet", tr).parent().prop("disabled", true);
			$(this).on("change", function(){
				var tr = $(this).parent().parent();
				tr.removeClass("danger");
				$("input", tr).prop("disabled", false);
				$("button > span.glyphicon-retweet", tr).parent().prop("disabled", false);
				$("option", this).filter(function(i, el){
					return (allRooms.indexOf(el.value) == -1) && (el.value != "");
				}).remove();
			});
		}
	});
});