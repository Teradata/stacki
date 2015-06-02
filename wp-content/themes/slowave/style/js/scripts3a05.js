/*-----------------------------------------------------------------------------------*/
/*	SINGLE PAGER FIXES
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function($){

	$('.page-template-page_one_pager-php .dslc-modules-section').each(function(idx){
		idx = idx + 1;
		$(this).attr('id', 'section-' + idx);
	});
	
});
/*-----------------------------------------------------------------------------------*/
/*	DROPDOWN CART
/*-----------------------------------------------------------------------------------*/
jQuery(window).load(function($){
	
	jQuery('#ebor-cart-link').mouseenter(function(){
		jQuery(this).toggleClass('active');
		jQuery(".dropdowncartcontents").stop().slideToggle();
	});
	
	var top = jQuery('#shop-dropdown-marker').offset().top;
		
	jQuery('.dropdowncartcontents').css({
		'top' : top
	});
	
	jQuery(".dropdowncartcontents").css({
		'left' : jQuery('#shop-dropdown-marker').offset().left - 280
	});
	
	jQuery(window).resize(function(){
		jQuery(".dropdowncartcontents").css({
			'left' : jQuery('#shop-dropdown-marker').offset().left - 280
		});
	});
	
	jQuery(window).scroll(function(){
		var scrollTop = jQuery(window).scrollTop();
		
		adminTop = 0;
		
		if( jQuery('body').hasClass('admin-bar') )
			adminTop = adminTop + 28;
			
		if( scrollTop < top ){
			jQuery('.dropdowncartcontents').css({
				'top' : top - scrollTop
			});
		} else {
			jQuery('.dropdowncartcontents').css({
				'top' : jQuery('.yamm.navbar.fixed').height() + adminTop
			});
		}
	});
	
});
/*-----------------------------------------------------------------------------------*/
/*	MEGA MENU FIXES
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function ($) {
	$('.yamm-content').parents('ul.dropdown-menu').addClass('yamm-dropdown-menu').parent().addClass('yamm-fullwidth');
	$('p:empty').remove();
	
	/**
	 * Check for background images
	 */
	$('.dslc-modules-section').each(function(){
		if( $(this).css('background-image') !== 'none' )
			$(this).addClass('parallax');
	});
	
	/**
	 * Newsletter widget Fixes
	 */
	$('.widget_ns_mailchimp form label').each(function(){
		var text = $(this).text();
		$(this).next().attr('placeholder', text);
	});
	
});
/*-----------------------------------------------------------------------------------*/
/*	OWL CAROUSEL
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    
     jQuery(".owlcarousel").owlCarousel({
        navigation: true,
        navigationText : ['<i class="icon-left-open"></i>','<i class="icon-right-open"></i>'],
        pagination: false,
        rewindNav: false,
        items: 3,
        mouseDrag: true,
        itemsDesktop: [1200, 3],
        itemsDesktopSmall: [1024, 3],
        itemsTablet: [970, 2],
        itemsMobile: [767, 1]
    });
    
    var pagination = jQuery(".owl-clients").attr('data-pagination');
	
	if( "false" === pagination ){
	    jQuery(".owl-clients").owlCarousel({
	
	        autoPlay: 9000,
	        rewindNav: false,
	        items: 6,
	        itemsDesktop: [1200, 6],
	        itemsDesktopSmall: [1024, 4],
	        itemsTablet: [768, 3],
	        itemsMobile: [480, 2],
	        navigation: false,
	        pagination: false
	
	    });
	} else {
		jQuery(".owl-clients").owlCarousel({
		
	        autoPlay: 9000,
	        rewindNav: false,
	        items: 6,
	        itemsDesktop: [1200, 6],
	        itemsDesktopSmall: [1024, 4],
	        itemsTablet: [768, 3],
	        itemsMobile: [480, 2],
	        navigation: false,
	        pagination: true
	
	    });
	}
    
    var owl = jQuery(".owl-portfolio-slider");

    owl.owlCarousel({
        navigation: false,
        autoHeight: true,
        slideSpeed: 300,
        paginationSpeed: 400,
        singleItem: true
    });

    // Custom Navigation Events
    jQuery(".slider-next").click(function () {
        owl.trigger('owl.next');
    });
    jQuery(".slider-prev").click(function () {
        owl.trigger('owl.prev');
    });

});
/*-----------------------------------------------------------------------------------*/
/*	FANCYBOX
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    jQuery(".fancybox-media").fancybox({
        arrows: true,
        padding: 0,
        closeBtn: true,
        openEffect: 'fade',
        closeEffect: 'fade',
        prevEffect: 'fade',
        nextEffect: 'fade',
        helpers: {
            media: {},
            overlay: {
                locked: false
            },
            buttons: false,
            thumbs: {
                width: 50,
                height: 50
            },
            title: {
                type: 'inside'
            }
        },
        beforeLoad: function () {
            var el, id = jQuery(this.element).data('title-id');
            if (id) {
                el = jQuery('#' + id);
                if (el.length) {
                    this.title = el.html();
                }
            }
        }
    });
});
/*-----------------------------------------------------------------------------------*/
/*	TABS
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    jQuery('.tabs.services').easytabs({
        animationSpeed: 300,
        updateHash: false,
        cycle: 5000
    });
});
/*-----------------------------------------------------------------------------------*/
/*	TESTIMONIALS
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    jQuery('#testimonials').easytabs({
        animationSpeed: 500,
        updateHash: false,
        cycle: 5000
    });
});
/*-----------------------------------------------------------------------------------*/
/*	GO TO TOP
/*-----------------------------------------------------------------------------------*/
! function (a, b, c) {
    a.fn.scrollUp = function (b) {
        a.data(c.body, "scrollUp") || (a.data(c.body, "scrollUp", !0), a.fn.scrollUp.init(b))
    }, a.fn.scrollUp.init = function (d) {
        var e = a.fn.scrollUp.settings = a.extend({}, a.fn.scrollUp.defaults, d),
            f = e.scrollTitle ? e.scrollTitle : e.scrollText,
            g = a("<a/>", {
                id: e.scrollName,
                href: "#top",
                title: f
            }).appendTo("body");
        e.scrollImg || g.html(e.scrollText), g.css({
            display: "none",
            position: "fixed",
            zIndex: e.zIndex
        }), e.activeOverlay && a("<div/>", {
            id: e.scrollName + "-active"
        }).css({
            position: "absolute",
            top: e.scrollDistance + "px",
            width: "100%",
            borderTop: "1px dotted" + e.activeOverlay,
            zIndex: e.zIndex
        }).appendTo("body"), scrollEvent = a(b).scroll(function () {
            switch (scrollDis = "top" === e.scrollFrom ? e.scrollDistance : a(c).height() - a(b).height() - e.scrollDistance, e.animation) {
            case "fade":
                a(a(b).scrollTop() > scrollDis ? g.fadeIn(e.animationInSpeed) : g.fadeOut(e.animationOutSpeed));
                break;
            case "slide":
                a(a(b).scrollTop() > scrollDis ? g.slideDown(e.animationInSpeed) : g.slideUp(e.animationOutSpeed));
                break;
            default:
                a(a(b).scrollTop() > scrollDis ? g.show(0) : g.hide(0))
            }
        }), g.click(function (b) {
            b.preventDefault(), a("html, body").animate({
                scrollTop: 0
            }, e.topSpeed, e.easingType)
        })
    }, a.fn.scrollUp.defaults = {
        scrollName: "scrollUp",
        scrollDistance: 300,
        scrollFrom: "top",
        scrollSpeed: 300,
        easingType: "linear",
        animation: "fade",
        animationInSpeed: 200,
        animationOutSpeed: 200,
        scrollText: "Scroll to top",
        scrollTitle: !1,
        scrollImg: !1,
        activeOverlay: !1,
        zIndex: 2147483647
    }, a.fn.scrollUp.destroy = function (d) {
        a.removeData(c.body, "scrollUp"), a("#" + a.fn.scrollUp.settings.scrollName).remove(), a("#" + a.fn.scrollUp.settings.scrollName + "-active").remove(), a.fn.jquery.split(".")[1] >= 7 ? a(b).off("scroll", d) : a(b).unbind("scroll", d)
    }, a.scrollUp = a.fn.scrollUp
}(jQuery, window, document);

jQuery(document).ready(function () {
    jQuery.scrollUp({
        scrollName: 'scrollUp', // Element ID
        scrollDistance: 300, // Distance from top/bottom before showing element (px)
        scrollFrom: 'top', // 'top' or 'bottom'
        scrollSpeed: 300, // Speed back to top (ms)
        easingType: 'linear', // Scroll to top easing (see http://easings.net/)
        animation: 'fade', // Fade, slide, none
        animationInSpeed: 200, // Animation in speed (ms)
        animationOutSpeed: 200, // Animation out speed (ms)
        scrollText: '<i class="icon-up-open"></i>', // Text for element, can contain HTML
        scrollTitle: false, // Set a custom <a> title if required. Defaults to scrollText
        scrollImg: false, // Set true to use image
        activeOverlay: false, // Set CSS color to display scrollUp active point, e.g '#00FFFF'
        zIndex: 1001 // Z-Index for the overlay
    });
});
/*-----------------------------------------------------------------------------------*/
/*	MENU
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    jQuery('.js-activated').dropdownHover({
        instantlyCloseOthers: false,
        delay: 0
    }).dropdown();


    jQuery('.dropdown-menu a, .social .dropdown-menu, .social .dropdown-menu input').click(function (e) {
        e.stopPropagation();
    });

});
/*-----------------------------------------------------------------------------------*/
/*	ISOTOPE PORTFOLIO
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    var $container = jQuery('.items');
    $container.imagesLoaded(function () {
        $container.isotope({
            itemSelector: '.item',
            layoutMode: 'fitRows'
        });
    });

    jQuery('.portfolio .filter li a').click(function () {

        jQuery('.portfolio .filter li a').removeClass('active');
        jQuery(this).addClass('active');

        var selector = jQuery(this).attr('data-filter');
        $container.isotope({
            filter: selector
        });

        return false;
    });
});
/*-----------------------------------------------------------------------------------*/
/*	ISOTOPE GRID BLOG
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    var $container = jQuery('.grid-blog');
    $container.imagesLoaded(function () {
        $container.isotope({
            itemSelector: '.post'
        });
    });

    jQuery(window).on('resize', function () {
        jQuery('.grid-blog').isotope('reLayout')
    });
});
/*-----------------------------------------------------------------------------------*/
/*	ISOTOPE LATEST BLOG
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    var $container = jQuery('.latest-blog');
    $container.imagesLoaded(function () {
        $container.isotope({
            itemSelector: '.post',
            layoutMode: 'fitRows'
        });
    });

    jQuery(window).on('resize', function () {
        jQuery('.latest-blog').isotope('reLayout')
    });
});
/*-----------------------------------------------------------------------------------*/
/*	IMAGE HOVER
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    jQuery('.icon-overlay a').prepend('<span class="icn-more"></span>');
});
/*-----------------------------------------------------------------------------------*/
/*	PRETTIFY
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    window.prettyPrint && prettyPrint()
});
/*-----------------------------------------------------------------------------------*/
/*	DATA REL
/*-----------------------------------------------------------------------------------*/
jQuery('a[data-rel]').each(function () {
    jQuery(this).attr('rel', jQuery(this).data('rel'));
});
/*-----------------------------------------------------------------------------------*/
/*	VIDEO
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    jQuery('.player').fitVids();
});
/*-----------------------------------------------------------------------------------*/
/*	PARALLAX MOBILE
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    if (navigator.userAgent.match(/Android/i) ||
        navigator.userAgent.match(/webOS/i) ||
        navigator.userAgent.match(/iPhone/i) ||
        navigator.userAgent.match(/iPad/i) ||
        navigator.userAgent.match(/iPod/i) ||
        navigator.userAgent.match(/BlackBerry/i)) {
        jQuery('.parallax').addClass('mobile');
    }
});
/*-----------------------------------------------------------------------------------*/
/*	TOOLTIP
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {
    if (jQuery("[rel=tooltip]").length) {
        jQuery("[rel=tooltip]").tooltip();
    }
});
/*-----------------------------------------------------------------------------------*/
/*	STICKY NAVIGATION
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function () {

    var menu = jQuery('.navbar'),
        pos = menu.offset();

    jQuery(window).scroll(function () {
        if (jQuery(this).scrollTop() > pos.top + menu.height() && menu.hasClass('default') && jQuery(this).scrollTop() > 150) {
            menu.fadeOut('fast', function () {
                jQuery(this).removeClass('default').addClass('fixed').fadeIn('fast');
            });
        } else if (jQuery(this).scrollTop() <= pos.top + 150 && menu.hasClass('fixed')) {
            menu.fadeOut(0, function () {
                jQuery(this).removeClass('fixed').addClass('default').fadeIn(0);
            });
        }
    });

});
jQuery(document).ready(function() {
	jQuery('.offset').css('padding-top', jQuery('.navbar').height() + 'px');
       
}); 
jQuery(window).resize(function() {
	jQuery('.offset').css('padding-top', jQuery('.navbar').height() + 'px');        
}); 
/*-----------------------------------------------------------------------------------*/
/*	ONEPAGE ANCHOR SCROLL
/*-----------------------------------------------------------------------------------*/
/**
* jQuery.LocalScroll - Animated scrolling navigation, using anchors.
* Copyright (c) 2007-2009 Ariel Flesler - aflesler(at)gmail(dot)com | http://flesler.blogspot.com
* Dual licensed under MIT and GPL.
* Date: 3/11/2009
* @author Ariel Flesler
* @version 1.2.7
**/
(function($){var l=location.href.replace(/#.*/,'');var g=jQuery.localScroll=function(a){jQuery('body').localScroll(a)};g.defaults={duration:1e3,axis:'y',event:'click',stop:true,target:window,reset:true};g.hash=function(a){if(location.hash){a=jQuery.extend({},g.defaults,a);a.hash=false;if(a.reset){var e=a.duration;delete a.duration;jQuery(a.target).scrollTo(0,a);a.duration=e}i(0,location,a)}};jQuery.fn.localScroll=function(b){b=jQuery.extend({},g.defaults,b);return b.lazy?this.bind(b.event,function(a){var e=jQuery([a.target,a.target.parentNode]).filter(d)[0];if(e)i(a,e,b)}):this.find('a,area').filter(d).bind(b.event,function(a){i(a,this,b)}).end().end();function d(){return!!this.href&&!!this.hash&&this.href.replace(this.hash,'')==l&&(!b.filter||jQuery(this).is(b.filter))}};function i(a,e,b){var d=e.hash.slice(1),f=document.getElementById(d)||document.getElementsByName(d)[0];if(!f)return;if(a)a.preventDefault();var h=jQuery(b.target);if(b.lock&&h.is(':animated')||b.onBefore&&b.onBefore.call(b,a,f,h)===false)return;if(b.stop)h.stop(true);if(b.hash){var j=f.id==d?'id':'name',k=jQuery('<a> </a>').attr(j,d).css({position:'absolute',top:jQuery(window).scrollTop(),left:jQuery(window).scrollLeft()});f[j]='';jQuery('body').prepend(k);location=e.hash;k.remove();f[j]=d}h.scrollTo(f,b).trigger('notify.serialScroll',[f])}})(jQuery);
/**
 * Copyright (c) 2007-2012 Ariel Flesler - aflesler(at)gmail(dot)com | http://flesler.blogspot.com
 * Dual licensed under MIT and GPL.
 * @author Ariel Flesler
 * @version 1.4.5 BETA
 */
;(function($){var h=jQuery.scrollTo=function(a,b,c){jQuery(window).scrollTo(a,b,c)};h.defaults={axis:'xy',duration:parseFloat(jQuery.fn.jquery)>=1.3?0:1,limit:true};h.window=function(a){return jQuery(window)._scrollable()};jQuery.fn._scrollable=function(){return this.map(function(){var a=this,isWin=!a.nodeName||jQuery.inArray(a.nodeName.toLowerCase(),['iframe','#document','html','body'])!=-1;if(!isWin)return a;var b=(a.contentWindow||a).document||a.ownerDocument||a;return/webkit/i.test(navigator.userAgent)||b.compatMode=='BackCompat'?b.body:b.documentElement})};jQuery.fn.scrollTo=function(e,f,g){if(typeof f=='object'){g=f;f=0}if(typeof g=='function')g={onAfter:g};if(e=='max')e=9e9;g=jQuery.extend({},h.defaults,g);f=f||g.duration;g.queue=g.queue&&g.axis.length>1;if(g.queue)f/=2;g.offset=both(g.offset);g.over=both(g.over);return this._scrollable().each(function(){if(e==null)return;var d=this,$elem=jQuery(d),targ=e,toff,attr={},win=$elem.is('html,body');switch(typeof targ){case'number':case'string':if(/^([+-]=?)?\d+(\.\d+)?(px|%)?$/.test(targ)){targ=both(targ);break}targ=jQuery(targ,this);if(!targ.length)return;case'object':if(targ.is||targ.style)toff=(targ=jQuery(targ)).offset()}jQuery.each(g.axis.split(''),function(i,a){var b=a=='x'?'Left':'Top',pos=b.toLowerCase(),key='scroll'+b,old=d[key],max=h.max(d,a);if(toff){attr[key]=toff[pos]+(win?0:old-$elem.offset()[pos]);if(g.margin){attr[key]-=parseInt(targ.css('margin'+b))||0;attr[key]-=parseInt(targ.css('border'+b+'Width'))||0}attr[key]+=g.offset[pos]||0;if(g.over[pos])attr[key]+=targ[a=='x'?'width':'height']()*g.over[pos]}else{var c=targ[pos];attr[key]=c.slice&&c.slice(-1)=='%'?parseFloat(c)/100*max:c}if(g.limit&&/^\d+$/.test(attr[key]))attr[key]=attr[key]<=0?0:Math.min(attr[key],max);if(!i&&g.queue){if(old!=attr[key])animate(g.onAfterFirst);delete attr[key]}});animate(g.onAfter);function animate(a){$elem.animate(attr,f,g.easing,a&&function(){a.call(this,e,g)})}}).end()};h.max=function(a,b){var c=b=='x'?'Width':'Height',scroll='scroll'+c;if(!jQuery(a).is('html,body'))return a[scroll]-jQuery(a)[c.toLowerCase()]();var d='client'+c,html=a.ownerDocument.documentElement,body=a.ownerDocument.body;return Math.max(html[scroll],body[scroll])-Math.min(html[d],body[d])};function both(a){return typeof a=='object'?a:{top:a,left:a}}})(jQuery);
jQuery(document).ready(function(){ 
	if( jQuery('body').hasClass('page-template-page_one_pager-php') ){
	
	    jQuery('.page-template-page_one_pager-php .scroll, .page-template-page_one_pager-php .navbar .nav').localScroll({
		    offset: {top:-58, left:0}
	    });
		jQuery('.page-template-page_one_pager-php .nav li a').on('click',function(){
		    jQuery('.page-template-page_one_pager-php .navbar-collapse.in').collapse('hide');
		});
	
	}
});
/*-----------------------------------------------------------------------------------*/
/*	SCROLL NAV
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function() {
	if( jQuery('body').hasClass('page-template-page_one_pager-php') ){
	
		headerWrapper = parseInt(jQuery('.navbar').height());
		offsetTolerance	= -42;
		
		//Detecting user's scroll
		jQuery(window).scroll(function() {
		
			//Check scroll position
			scrollPosition	= parseInt(jQuery(this).scrollTop());
			
			//Move trough each menu and check its position with scroll position then add current class
			jQuery('.navbar ul a[href^="#"]').each(function() {
	
				thisHref				= jQuery(this).attr('href');
				thisTruePosition	= parseInt(jQuery(thisHref).offset().top);
				thisPosition 		= thisTruePosition - headerWrapper - offsetTolerance;
				
				if(scrollPosition >= thisPosition) {
					
					jQuery('.current').removeClass('current');
					jQuery('.navbar ul a[href='+ thisHref +']').parent('li').addClass('current');
					
				}
			});
			
			
			//If we're at the bottom of the page, move pointer to the last section
			bottomPage	= parseInt(jQuery(document).height()) - parseInt(jQuery(window).height());
			
			if(scrollPosition == bottomPage || scrollPosition >= bottomPage) {
			
				jQuery('.current').removeClass('current');
				jQuery('.navbar ul a:last').parent('li').addClass('current');
			}
		});
	
	}
	
	jQuery('a.scroller').click(function(){
		var url = jQuery(this).attr('href');
		jQuery("html, body").animate({ scrollTop: jQuery(url).offset().top - 58 }, 1000);
		return false;
	});
});
/*-----------------------------------------------------------------------------------*/
/*	NAV BASE LINK
/*-----------------------------------------------------------------------------------*/
jQuery(document).ready(function($) {

	jQuery('a.js-activated').not('a.js-activated[href^="#"]').click(function(){
		var url = $(this).attr('href');
		window.location.href = url;
		return true;
	});
		
});