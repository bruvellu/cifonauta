$(document).ready(function () {
    function updateIsPublic() {
        var status = $("#id_status").val();
        var isPublicField = $("#id_is_public");

        if (status === "published") {
            
            isPublicField.prop("checked", true);
            
        } else {
            isPublicField.prop("checked", false);
        }
    }

    updateIsPublic();

    $("#id_status").change(updateIsPublic);
});
