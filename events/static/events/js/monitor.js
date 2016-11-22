function adjustIndicatorWidth(carousel)
{
	var width = $(".item.active table", carousel).css("width");
	$(".carousel-indicators", carousel).animate({"width": width}, 50);
}

$(document).ready(function() {
	adjustIndicatorWidth($("#important-event-carousel"));
	adjustIndicatorWidth($("#other-event-carousel"));

	$("#important-event-carousel").on("slid.bs.carousel", function() {
		adjustIndicatorWidth($("#important-event-carousel"));
	});

	$("#other-event-carousel").on("slid.bs.carousel", function() {
		adjustIndicatorWidth($("#other-event-carousel"));
	});
});