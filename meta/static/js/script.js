// Document ready functions.
$(document).ready(function(){
    
    // Highslide
    // Esconde avisos.
    $(".success, .notice, .error").delay(10000).fadeOut('slow');

    // Trigger do seletor de línguas.
    $('#languages select').change(function () {
        var myform = $(this).parent();
        if ($(this).val() != "{{ request.LANGUAGE_CODE }}") {
            myform.submit();};
    });

});
