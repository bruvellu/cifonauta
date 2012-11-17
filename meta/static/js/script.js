// Load Disqus on demand.
function loadDisqus() {
  var url = $(location).attr("href");
  $("#comments p").load(url);
  return false;
}

// jQuery Treeview.
var treeview = $("#colaptree").treeview({
  collapsed: true,
  animated: "fast",
  persist: "location",
});
function open_tree(taxas){
	// Close all tree
	$('ul.treeview li div.collapsable-hitarea').click();
	$.each((taxas.split(',')), function(index){
		$('#taxa' + this).parents('li').children('div.expandable-hitarea').click()
	});
};


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
  defered.async = true;
  var holder = document.getElementById("deferedjs");
  holder.parentNode.insertBefore(defered, holder);
}

//Social
var social = $("#intro");
if (social.length > 0) {
    // Twitter button.
    loadSocial("//platform.twitter.com/widgets.js");

    // Google Plus button
    loadSocial("//apis.google.com/js/plusone.js");

    // Facebook Like button
    loadSocial("//connect.facebook.net/en_US/all.js#xfbml=1");
}


// Add2Any button
var media = $("#media-page");
if (media.length > 0) {
    function my_addtoany_onready() {
    a2a_config.target = '.share-this';
    a2a.init('page');
    }
    // Setup AddToAny "onReady" callback
    var a2a_config = a2a_config || {};
    a2a_config.tracking_callback = {
    ready: my_addtoany_onready
    };
    // Load AddToAny script asynchronously
    loadSocial("//static.addtoany.com/menu/page.js");
}

// Document ready functions.
$(document).ready(function(){

  // External DB hovers
  $(".biodb li").hover(
    function () { $(this).find(".external").fadeIn(200); },
    function () { $(this).find(".external").fadeOut(200); }
    );

  // Disqus
  $('#comments p').click(loadDisqus);

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
