document.addEventListener("DOMContentLoaded", function () {
    var selectedCurationGet = document.getElementById("selected_curation_id_get");
    var selectedCurationPost = document.getElementById("selected_curation_id_post");
    selectedCurationGet.addEventListener("change", function () {
        selectedCurationPost.value = selectedCurationGet.value;
    });
});