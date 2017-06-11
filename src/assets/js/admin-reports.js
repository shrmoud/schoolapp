(function($) {
    $( document ).ready(function() {
	    var button = $('input[name=_save]');
	    button.val('Return');
	    button.click(function(event) {
	        event.preventDefault();
	        window.history.back();
	    });
	});
})(django.jQuery);
    