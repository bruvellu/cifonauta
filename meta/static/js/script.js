// Treeview
$("#colaptree").treeview({
    collapsed: true,
    animated: "fast",
    persist: "location",
});

// Load Disqus on demand.
function load_disqus() {
    var url = $(location).attr("href");
    $("#comments").load(url);
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
    $('#comments').click(load_disqus);

    // Esconde avisos.
    $(".success, .notice, .error").delay(10000).fadeOut('slow');

    // Trigger do seletor de línguas.
    $('#languages select').change(function () {
        var myform = $(this).parent();
        if ($(this).val() != "{{ request.LANGUAGE_CODE }}") {
            myform.submit();};
    });

});


