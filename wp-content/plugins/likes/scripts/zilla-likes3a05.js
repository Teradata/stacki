jQuery(document).ready(function($){

	$('.zilla-likes').live('click',
	    function() {
    		var link = $(this);
    		if(link.hasClass('active')) return false;
		
    		var id = $(this).attr('id'),
    			postfix = link.find('.zilla-likes-postfix').text();
			
    		$.post(zilla_likes.ajaxurl, { action:'zilla-likes', likes_id:id, postfix:postfix }, function(data){
    			link.html(data).addClass('active').attr('title','You already like this');
    		});
		
    		return false;
	});
	
	if( $('body.ajax-zilla-likes').length ) {
        $('.zilla-likes').each(function(){
    		var id = $(this).attr('id');
    		$(this).load(zilla.ajaxurl, { action:'zilla-likes', post_id:id });
    	});
	}

});