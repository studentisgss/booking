
  // Let the possibility to modify address if javascipt is enabled
  // and disable the address form so only fillInAddress can fill it
  $(document).ready(function(){
    $("#address-form").removeClass("d-none");
    $("#address-message").remove();
    $("#id_address").prop('readonly', true);

    function updateGeocoderProximity() {
        // proximity is designed for local scale, if the user is looking at the whole world,
        // it doesn't make sense to factor in the arbitrary centre of the map
        if (map.getZoom() > 9) {
            var center = map.getCenter().wrap(); // ensures the longitude falls within -180 to 180 as the Geocoding API doesn't accept values outside this range
            geocoder.setProximity({ longitude: center.lng, latitude: center.lat });
        } else {
            geocoder.setProximity(null);
        }
    }

  var map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v11',
  center: [11.8874945, 45.4050894],
  zoom: 13
  });

  var geocoder = new MapboxGeocoder({
  accessToken: mapboxgl.accessToken
  });

  document.getElementById('locationField').appendChild(geocoder.onAdd(map));

  // After the map style has loaded on the page, add a source layer and default
  // styling for a single point.
  map.on('load', function() {
    updateGeocoderProximity()
  map.addSource('single-point', {
  "type": "geojson",
  "data": {
  "type": "FeatureCollection",
  "features": []
  }
  });

  map.addLayer({
  "id": "point",
  "source": "single-point",
  "type": "circle",
  "paint": {
  "circle-radius": 10,
  "circle-color": "#007cbf"
  }
  });

  // Listen for the `result` event from the MapboxGeocoder that is triggered when a user
  // makes a selection and add a symbol that matches the result.
  geocoder.on('result', function(ev) {
  map.getSource('single-point').setData(ev.result.geometry);
  document.getElementById("id_address").value = ev.result.place_name;
  });
  map.on('moveend', updateGeocoderProximity);
  });
});
