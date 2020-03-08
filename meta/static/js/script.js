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

// FIXME: This was closing the open tree! Not sure what it is for.
//function open_tree(taxas){
	//// Close all tree
	//$('ul.treeview li div.collapsable-hitarea').click();
	//$.each((taxas.split(',')), function(index){
		//$('#taxa' + this).parents('li').children('div.expandable-hitarea').click()
	//});
//};

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

  // Disqus
  $('#comments p').click(loadDisqus);

  // FIXME: Esconde árvore?
  //$("#colaptree").delay(400).fadeIn('slow');

  // Esconde avisos.
  $(".success, .notice, .error").delay(10000).fadeOut('slow');

  // Trigger do seletor de línguas.
  $('#languages select').change(function () {
    var myform = $(this).parent();
    myform.submit();
  });

});
