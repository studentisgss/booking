
  // Let the possibility to modify address if javascipt is enabled
  // and disable the address form so only fillInAddress can fill it
  $(document).ready(function(){
    $("#address-form").removeClass("d-none");
    $("#address-message").remove();
    $("#id_address").prop('readonly', true);
  });

  // Fill the address using the Google Maps API
  var placeSearch, autocomplete, map, marker;

  function initAutocomplete() {
    var input = document.getElementById('autocomplete');
    // Create the autocomplete object.
    autocomplete = new google.maps.places.Autocomplete(
        /** @type {!HTMLInputElement} */(input),
        {types: ['address']});
    // Crate the maps centered at Collegio Morgagni 45.4050894,11.8874945; zoom 14 center in the address if edit
    map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: 45.4050894, lng: 11.8874945},
      zoom: 14
    });
    // Center the map at the existing address of the building
    // (if we are creating a new building will remani the address of Coleggio Morgagni)
    var geocoder = new google.maps.Geocoder();
    // take the address from the form
    var address = document.getElementById('id_address').value;
    geocoder.geocode({'address': address}, function(results, status) {
      if (status === 'OK') {
        map.setCenter(results[0].geometry.location);
        map.setZoom(17);
        // inizialize the marker whit the address
        marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
        });
      } else {
      // inizialize the marker
        marker = new google.maps.Marker({
          map: map,
          anchorPoint: new google.maps.Point(0, -29)
        });
      }
    });
    // Bind the map's bounds (viewport) property to the autocomplete object,
    // so that the autocomplete requests use the current map bounds for the
    // bounds option in the request.
    autocomplete.bindTo('bounds', map);
    // When the user selects an address from the dropdown, populate the address form
    // and recenter the map
    autocomplete.addListener('place_changed', fillInAddress);
  }

    function fillInAddress() {
    marker.setVisible(false);
    // Get the place details from the autocomplete object.
    var place = autocomplete.getPlace();
    if (!place.geometry) {
      // User entered the name of a Place that was not suggested and
      // pressed the Enter key, or the Place Details request failed.
      window.alert("Spiacenti: '" + place.name + "' non è stato trovato. Riprova.");
      return;
    }
    // If the place has a geometry, then present it on a map.
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry.location);
      map.setZoom(17);  // Why 17? Because it looks good.
    }
    marker.setPosition(place.geometry.location);
    marker.setVisible(true);
    // Get the address from the place details and fill the form.
    document.getElementById("id_address").value=place.formatted_address;
  }
