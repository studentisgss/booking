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
	span.parent().on("click", function(){
		$(this).siblings("input").prop("checked", true);
		$(this).parent().parent().fadeOut();
	});
});