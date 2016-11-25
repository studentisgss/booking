$(document).ready(function() {
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
});