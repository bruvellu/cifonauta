const referenceModal = new Modal({
    modalContent: document.querySelector('[data-modal="latitude"]'),
    modalTrigger: document.querySelector('[data-open-modal="latitude"]'),
    modalClose: document.querySelector('[data-close-modal="latitude"]')
})
function myMap() {

window.lat = document.getElementById("id_latitude").value
window.lng = document.getElementById("id_longitude").value

if (window.lat == '' || window.lng == ''){
    lat = -23.828094
    lng = -45.421718
}
var latLngInitial = new google.maps.LatLng(lat,lng)
var mapProp= {
    center:latLngInitial,
    zoom:10,
    gestureHandling: "greedy",
    streetViewControl: false,
    fullscreenControl: false,
};
var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
window.marker = new google.maps.Marker({
    position: latLngInitial,
    map: map,
    });

map.addListener("click", (e) => {
    placeMarkerAndPanTo(e.latLng, map);
    });
}

function placeMarkerAndPanTo(latLng, map) {
    marker.setMap(null);
    marker = new google.maps.Marker({
    position: latLng,
    map: map,
    });
    document.getElementById("id_latitude").value = latLng.lat();
    document.getElementById("id_longitude").value = latLng.lng();

    map.panTo(latLng);
    referenceModal.closeModal()
}
    