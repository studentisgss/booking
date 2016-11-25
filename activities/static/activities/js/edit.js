$(document).ready(function() {
	$("select.form-control").on("change", function(){
		if (waitingRooms.indexOf(this.value) > -1)
		{
			var tr = $(this).parent().parent()
			tr.addClass("warning");
			tr.attr("title", "Questa prenotazione verrà messa in attesa di approvazione.");
		}
		else
		{
			$(this).removeClass("bg-warning");
			$(this).attr("title", "");
		}
	});
});