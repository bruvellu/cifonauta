// jQuery Treeview.
var treeview = $("#tree").treeview({
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

// Document ready functions.
$(document).ready(function(){

  // External DB hovers
  $(".biodb li").hover(
    function () { $(this).find(".external").fadeIn(200); },
    function () { $(this).find(".external").fadeOut(200); }
    );

  // Esconde avisos.
  $(".success, .notice, .error").delay(10000).fadeOut('slow');

  // Trigger for language selector
  $('#nav-languages select').change(function () {
    var langform = $(this).parent();
    langform.submit();
  });

});
