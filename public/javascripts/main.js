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
});