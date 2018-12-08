function adjustIndicatorWidth()
{
	// Set carousel indicator width
	var array = $(".carousel-item table").map(function(){
		var clone = $(this).clone();
		clone.css("visibility","d-none");
    	$('body').append(clone);
		var res = parseInt(clone.width());
		clone.remove();
		return res;
	});
	var width = Math.max(...array);
	$(".carousel-indicators").css("width", width + "px");

	// Set all table to the same width
	// but do not chenge the width of the first cell
	$.each($(".carousel td:not(.head):even"), function(){
		var clone = $(this).clone();
		clone.css("visibility","d-none");
    	$('body').append(clone);
		$(this).data("width", clone.css("width"));
		clone.remove();
	});
	$(".carousel table").css("width", width + "px");
	$.each($(".carousel td:not(.head):even"), function(){
		$(this).css("width", $(this).data("width"));
	});
}

$(document).ready(function() {
	adjustIndicatorWidth();
});
