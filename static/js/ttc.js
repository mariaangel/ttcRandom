
var x;
var lat, lon;


function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showStops, showError);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showStops(position) {
    lat = position.coords.latitude
    lon = position.coords.longitude

    $.ajax({
        type: "GET",
        url:  "/getStops?lat=" + lat + "&lon=" + lon,
        dataType: 'json',
        success: function(results){
            if (results.error){
                $('#error').hide().html("<span class=\"text-danger\"> Error: " + results.error + "</span>").fadeIn('slow');
            }
            else{
                map();
                $('#stops').html(' ');
                $('#stops').append('<form action="/getDeparture" method="post"><div id="bItems"></div></form>');
                $.each( results, function(i, obj) {
                $('#bItems').append('<input type="hidden" name="'+ i +'" value="'+ obj[0] +'">');
                var res = '<button class="btn btn-primary btn-lg btn-block" type="submit" \
                    id="' + i + '" name="stop" value="' + i + '">' + i.replace(/_/g, ' ') + ' </button>';
                $('#bItems').hide().append(res).fadeIn('slow');
                mapMarker(i,obj[0],obj[1])
                });

            }
        },
        error: function(xhr, text, error){
                console.log("readyState: " + xhr.readyState);
                console.log("responseText: "+ xhr.responseText);
                console.log("status: " + xhr.status);
                console.log("text status: " + text);
                console.log("error: " + error);
            res = jQuery.parseJSON(xhr.responseText);
            $('#stops').hide().append("<span class=\"text-danger\"> Error: " + res.error + "</span>").fadeIn('slow');
        }
    });

}

//from W3Schools
function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            x.innerHTML = "User denied the request for Geolocation."
            break;
        case error.POSITION_UNAVAILABLE:
            x.innerHTML = "Location information is unavailable."
            break;
        case error.TIMEOUT:
            x.innerHTML = "The request to get user location timed out."
            break;
        case error.UNKNOWN_ERROR:
            x.innerHTML = "An unknown error occurred."
            break;
    }
}

var googleMap;

function map(id) {
  var myLatlng = new google.maps.LatLng(lat,lon);
  var mapOptions = {
    zoom: 16,
    center: myLatlng
  }
  googleMap = new google.maps.Map(document.getElementById('maps'), mapOptions);
}

function mapMarker(id,lat,lon){
  var myLatlng = new google.maps.LatLng(lat,lon);
  var marker = new google.maps.Marker({
      position: myLatlng,
      map: googleMap,
      title: id
  });
  googleMap.setCenter(myLatlng);
}


