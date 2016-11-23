function adjustIndicatorWidth()
{
	var array = $(".item table").map(function(){ 
		var clone = $(this).clone();
		clone.css("visibility","hidden");
    	$('body').append(clone);
		var res = parseInt(clone.width());
		clone.remove();
		return res;
	});
	var width = Math.max(...array);
	$(".carousel-indicators").css("width", width + "px");
}

$(document).ready(function() {
	adjustIndicatorWidth();
});