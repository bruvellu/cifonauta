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

    // Share This
    var switchTo5x=true;
    $.getScript("http://w.sharethis.com/button/buttons.js");
    stLight.options({
        publisher:'c581e214-c1ef-43a0-9fa6-ce8c0de234df',
        tracking:'google',
        onhover:false,
    });

});


