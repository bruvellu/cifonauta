// Load Disqus on demand.
function load_disqus() {
    var url = $(location).attr("href");
    $("#comments p").load(url);
    return false;
}

// jQuery Treeview.
$("#colaptree").treeview({
      collapsed: true,
      animated: "fast",
      persist: "location",
  });

// Highslide
hs.graphicsDir = '/static/js/highslide/graphics/';
hs.outlineType = 'rounded-white';
hs.align = 'center';
hs.showCredits = false;


// Add VideoJS to all video tags on the page when the DOM is ready
VideoJS.setupAllWhenReady({
  returnToStart: true,
});

// Slides for tour
$('#slides').slides({
  preload: true,
  preloadImage: '/static/js/slides/loading.gif',
  autoHeight: true,
  play: 4000,
  hoverPause: true,
  slideSpeed: 300,
  generatePagination: false
});

function loadSocial(script) {
  var defered = document.createElement("script");
  defered.type = "text/javascript";
  defered.src = script;
  var holder = document.getElementById("deferedjs");
  holder.parentNode.insertBefore(defered, holder);
}

// Twitter button.
loadSocial("http://platform.twitter.com/widgets.js");

//var b = document.createElement('script');
//b.type = 'text/javascript';
//b.src = ('http://platform.twitter.com/widgets.js');
//var a=document.getElementById("deferedjs");
//a.parentNode.insertBefore(b,a);

// Google Plus button
loadSocial("https://apis.google.com/js/plusone.js");

//var po = document.createElement('script');
//po.type = 'text/javascript';
//po.async = true;
//po.src = 'https://apis.google.com/js/plusone.js';
//var s = document.getElementById('deferedjs');
//s.parentNode.insertBefore(po, s);

// Facebook Like button
loadSocial("//connect.facebook.net/en_US/all.js#xfbml=1");
//<div id="fb-root"></div>
//
//<script>(function(d, s, id) {
//  var js, fjs = d.getElementsByTagName(s)[0];
//  if (d.getElementById(id)) {return;}
//  js = d.createElement(s); js.id = id;
//  js.src = "//connect.facebook.net/pt_BR/all.js#xfbml=1";
//  fjs.parentNode.insertBefore(js, fjs);
//}(document, 'script', 'facebook-jssdk'));</script>

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
        myform.submit();
    });

});


