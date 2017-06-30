$(document).ready(function() {
  $('#annotate').click(function() {
     //$.get('/some/url', {foo: 42}, function(result) {
         $('.annotation .task').html('Is Immunization a controversial topic?');
     //});
  });
  $('.annotate-toggle').on('click',function(){
		$('.ui.sidebar')
		  .sidebar('setting', 'transition', 'overlay')
		  .sidebar('toggle')
		;
	});
  var call = window.location.hash.substr(1);
  if(call == 'annotate') {
    $('.ui.sidebar').sidebar('setting', 'transition', 'overlay').sidebar('toggle');
  }
  $('.pop').popup();
  $('.voting').on('click', function() {
    var data = {
      'entity' : $(this).attr('entity'),
      'vote' : $(this).attr('vote'),
      'location' : window.location.pathname
    }
    if($(this).attr('comment') !== undefined) {
      data['comment'] = $(this).attr('comment');
    }
    $.post( "/vote/", data );
    console.log(data);
 });
});