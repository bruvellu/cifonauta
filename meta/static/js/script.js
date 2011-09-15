// Load Disqus on demand.
function load_disqus() {
    var url = $(location).attr("href");
    $("#comments p").load(url);
    return false;
}

// Document ready functions.
$(document).ready(function(){

    // External DB hovers
    $(".biodb li").hover(
        function () {
            $(this).find(".external").fadeIn(200);
        },
        function () {
            $(this).find(".external").fadeOut(200);
        }
    );

    // Disqus
    $('#comments p').click(load_disqus);

    // Esconde avisos.
    $("#colaptree").delay(400).fadeIn('slow');

    // Esconde avisos.
    $(".success, .notice, .error").delay(10000).fadeOut('slow');

    // Trigger do seletor de línguas.
    $('#languages select').change(function () {
        var myform = $(this).parent();
        if ($(this).val() != "{{ request.LANGUAGE_CODE }}") {
            myform.submit();};
    });

});


