// Treeview
$("#colaptree").treeview({
    collapsed: true,
    animated: "fast",
    persist: "location",
});

// Document ready functions.
$(document).ready(function(){

    // Esconde avisos.
    $(".success, .notice, .error").delay(10000).fadeOut('slow');

    // Trigger do seletor de línguas.
    $('#languages select').change(function () {
        var myform = $(this).parent();
        if ($(this).val() != "{{ request.LANGUAGE_CODE }}") {
            myform.submit();};
    });

});
