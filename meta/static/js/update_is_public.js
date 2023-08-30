$(document).ready(function () {
    // Function to update the "is_public" to false when the status is not "published"
    function updateIsPublic() {
        // Gets the current value of the status field in the form using its ID.
        var status = $("#id_status").val();
        var isPublicField = $("#id_is_public");

        // Checks if the value of the status field is "published" 
        if (status === "published") {
            
            // Sets the "checked" property of the is_public field to true, checking it.
            isPublicField.prop("checked", true);
            
        } else {
            // If the status is not "published," set is_public to false.
            isPublicField.prop("checked", false);
        }
    }

    // Calls the updateIsPublic function when the page loads and whenever the status changes.
    updateIsPublic();

    // Adds an event listener to the status field, so that the updateIsPublic function is called whenever the status is changed.
    $("#id_status").change(updateIsPublic);
});
