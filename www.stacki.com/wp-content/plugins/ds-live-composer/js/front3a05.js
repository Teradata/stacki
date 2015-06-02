/**
 * Table of Contents
 *
 * - dslc_carousel ( Initializes carousels )
 */

/**
 * Responsive Classes
 */

function dslc_responsive_classes() {

	var windowWidth = jQuery(window).width();
	var body = jQuery('body');

	body.removeClass( 'dslc-res-phone dslc-res-tablet dslc-res-smaller-monitor dslc-res-big' )

	if ( windowWidth >= 1024 && windowWidth < 1280 )
		body.addClass( 'dslc-res-smaller-monitor' );
	else if ( windowWidth >= 768 && windowWidth < 1024 )
		body.addClass( 'dslc-res-tablet' );
	else if ( windowWidth < 768 ) 
		body.addClass( 'dslc-res-phone' );
	else
		body.addClass( 'dslc-res-big' );

}

/** 
 * Init Accordion
 */

function dslc_init_accordion() {

	jQuery('.dslc-accordion').each(function(){

		var dslcAccordion = jQuery(this),
		dslcActive = jQuery( '.dslc-accordion-item:first-child', dslcAccordion ),
		dslcInactive = dslcActive.siblings('.dslc-accordion-item');

		dslcActive.addClass('dslc-active');
		dslcInactive.addClass('dslc-inactive');

		jQuery('.dslc-accordion-content', dslcInactive).hide();

	});

}

/** 
 * Init Lightbox
 *
 * @since 1.0
 */

function dslc_init_lightbox() {

	jQuery( '.dslc-lightbox-image' ).each(function(){

		jQuery(this).magnificPopup({ type:'image' });

	});

	jQuery( '.dslc-lightbox-gallery' ).each(function(){

		jQuery(this).magnificPopup({ delegate : 'a', type:'image', gallery:{ enabled: true } });

	});

}

/**
 * Initializes carousels
 *
 * @since 1.0
 */

function dslc_carousel() {

	// Loop through each carousel
	jQuery( '.dslc-carousel, .dslc-slider' ).each( function() {
		
		// Variables
		var carousel, container, defSettings, usrSettings, settings;

		// Elements
		carousel = jQuery( this );
		container = carousel.closest( '.dslc-module-front' );	

		// Default settings
		defSettings = {
			items : 4,
			pagination : true,
			singleItem : false,
			itemsScaleUp : false,
			slideSpeed : 200,
			paginationSpeed : 800,
			rewindSpeed : 1000,
			autoPlay : false,
			stopOnHover : false,
			lazyLoad : false,
			lazyFollow : true,
			autoHeight : false,
			mouseDrag : true,
			touchDrag : true,
			addClassActive : true,
			transitionStyle : 'fade',
			scrollPerPage : true
		};

		// Custom Settings
		usrSettings = {
			items : carousel.data( 'columns' ),
			pagination : carousel.data( 'pagination' ),
			itemsScaleUp : carousel.data( 'scale-up' ),
			slideSpeed : carousel.data( 'slide-speed' ),
			paginationSpeed : carousel.data( 'pagination-speed' ),
			rewindSpeed : carousel.data( 'rewind-speed' ),
			autoPlay : carousel.data( 'autoplay' ),
			stopOnHover : carousel.data( 'stop-on-hover' ),
			lazyLoad : carousel.data( 'lazy-load' ),
			lazyFollow : carousel.data( 'lazy-follow' ),
			autoHeight : carousel.data( 'flexible-height' ),
			mouseDrag : carousel.data( 'mouse-drag' ),
			touchDrag : carousel.data( 'touch-drag' ),
			addClassActive : carousel.data( 'active-class' ),
			transitionStyle : carousel.data( 'animation' ),
			scrollPerPage : carousel.data( 'scroll-per-page' )
		};

		// Merge default and custom settings
		settings = jQuery.extend( {}, defSettings, usrSettings );

		// If it's a slider set singleItem to true
		if ( carousel.hasClass( 'dslc-slider' ) || settings.items == 1 ) {
			settings.singleItem = true;
		}

		// If autoplay is 0 set to false
		if ( settings.autoPlay == 0 )
			settings.autoPlay = false;

		// Initialize
		carousel.owlCarousel({

			items : settings.items,
			pagination : settings.pagination,
			singleItem : settings.singleItem,
			itemsScaleUp : settings.itemsScaleUp,
			slideSpeed : settings.slideSpeed,
			paginationSpeed : settings.paginationSpeed,
			rewindSpeed : settings.rewindSpeed,
			autoPlay : settings.autoPlay,
			stopOnHover : settings.stopOnHover,
			lazyLoad : settings.lazyLoad,
			lazyFollow : settings.lazyFollow,
			mouseDrag : settings.mouseDrag,
			touchDrag : settings.touchDrag,
			scrollPerPage : settings.scrollPerPage,
			transitionStyle : settings.transitionStyle,
			autoHeight : settings.autoHeight,
			itemsDesktop : false,
			itemsDesktopSmall : false,
			itemsTablet : false,
			itemsMobile : [766,1],
			afterInit: function() {
				carousel.prev( '.dslc-loader' ).remove();
				carousel.css({
					opacity : 1,
					maxHeight : 'none'
				});
			}

		});

		// Previous
		jQuery( '.dslc-carousel-nav-next', container ).click( function(e) {
			e.preventDefault();
			carousel.data( 'owlCarousel' ).next();
		});

		// Next
		jQuery( '.dslc-carousel-nav-prev', container ).click( function(e) {
			e.preventDefault();
			carousel.data( 'owlCarousel' ).prev();
		});
		
	});

}






/**
 * Initiate Video
 */

 	function dslc_bg_video() {

 		jQuery('.dslc-bg-video').each(function(){
 			if ( ! jQuery(this).find( 'video' ).length ) {
 				jQuery(this).css({ opacity : 1 });
 			}
 		});
 		jQuery('.dslc-bg-video video').mediaelementplayer({
			loop: true,
			success: function(mediaElement, domObject) {

				mediaElement.addEventListener('loadeddata', function (e) {
					jQuery(domObject).closest('.dslc-bg-video').animate({ opacity : 1 }, 400);
				});

				mediaElement.play();
			}
		});

 	}

/**
 * Initiate Parallax
 */

 	function dslc_parallax() {

 		var dslcSpeed = 4;
		var dslcPos = (-window.pageXOffset / dslcSpeed) + "px " + (-window.pageYOffset / dslcSpeed) + "px";
		jQuery('.dslc-init-parallax').css({ backgroundPosition : dslcPos });

		window.onscroll = function() {
			var dslcSpeed = 4;
			var dslcPos = (-window.pageXOffset / dslcSpeed) + "px " + (-window.pageYOffset / dslcSpeed) + "px";
			jQuery('.dslc-init-parallax').css({ backgroundPosition : dslcPos });
		}

 	}


/**
 * Initiate Masonry
 */
function dslc_masonry( dslcWrapper, dslcAnimate ) {

	dslcWrapper = typeof dslcWrapper !== 'undefined' ? dslcWrapper : jQuery('body');
	dslcAnimate = typeof dslcAnimate !== 'undefined' ? dslcAnimate : false;

	jQuery('.dslc-init-masonry', dslcWrapper).each(function(){

		var dslcContainer, dslcSelector, dslcItems, dslcItemWidth, dslcContainerWidth, dslcGutterWidth;

		dslcContainer = jQuery(this);
		dslcSelector = '.dslc-masonry-item';
		dslcItemWidth = jQuery(dslcSelector, dslcContainer).outerWidth();
		dslcContainerWidth = jQuery(dslcContainer).outerWidth();
		dslcGutterWidth = dslcContainerWidth / 100 * 2.05;

		if ( dslcContainer.data('masonry') ) {

			jQuery(dslcContainer).masonry('destroy').masonry({
				gutter : dslcGutterWidth,
				itemSelector : dslcSelector
			});

			jQuery( dslcContainer ).find( '.dslc-post:not(.dslc-masonry-item)' ).hide();

			if ( dslcAnimate ) {

				jQuery(dslcSelector, dslcContainer).css({ 'scale' : '0.2'}).animate({ 
					'scale' : '1'
				}, 500);

			}

		} else {

			jQuery(dslcSelector).css({ marginRight : 0 });

			jQuery(dslcContainer).masonry({
				gutter : dslcGutterWidth,
				itemSelector : dslcSelector
			});

		}

	});

}

function dslc_browser_classes() {

	jQuery.each(jQuery.browser, function(i) {
	    jQuery('body').addClass(i);
	    return false;  
	});

	var os = [
	    'iphone',
	    'ipad',
	    'windows',
	    'mac',
	    'linux'
	];

	var match = navigator.appVersion.toLowerCase().match(new RegExp(os.join('|')));
	if (match) {
	    jQuery('body').addClass(match[0]);
	};

}

function dslc_center() {

	var dslcElement, dslcContainer, dslcElementHeight, dslcContainerHeight, dslcElementWidth, dslcContainerWidth, dslcTopOffset, dslcLeftOffset;

	jQuery('.dslc-init-center').each(function(){

		// Get elements
		dslcElement = jQuery(this);
		dslcContainer = dslcElement.parent();

		// Get height and width
		dslcElementWidth = dslcElement.outerWidth();
		dslcElementHeight = dslcElement.outerHeight();
		dslcContainerWidth = dslcContainer.outerWidth();
		dslcContainerHeight = dslcContainer.outerHeight();

		// Get center offset
		dslcTopOffset = dslcContainerHeight / 2 - dslcElementHeight / 2;
		dslcLeftOffset = dslcContainerWidth / 2 - dslcElementWidth / 2;

		// Apply offset
		if ( dslcTopOffset > 0 ) {
			dslcElement.css({ top : dslcTopOffset, left : dslcLeftOffset });
			dslcElement.css({ visibility : 'visible' });
		}		

	});

}

function dslc_init_square( dslcWrapper ) {

	dslcWrapper = typeof dslcWrapper !== 'undefined' ? dslcWrapper : jQuery('body');

	var dslcElement, dslcHeight, dslcWidth;

	jQuery('.dslc-init-square', dslcWrapper).each( function(){

		dslcElement = jQuery(this);
		dslcElement.css({ width : 'auto', height : 'auto' });
		dslcHeight = dslcElement.height();
		dslcWidth = dslcElement.width();

		if ( dslcHeight > dslcWidth )
			dslcElement.width( dslcHeight );
		else
			dslcElement.height( dslcWidth );

	});

}

/**
 * Tabs
 */

function dslc_tabs_generate_code( dslcTabs ) {

	var dslcTabsContainer = dslcTabs.closest('.dslc-module-front');

	dslcTabsNav = jQuery('.dslc-tabs-nav', dslcTabs);
	dslcTabsContent = jQuery('.dslc-tabs-content', dslcTabs);
	dslcTabContent = jQuery('.dslc-tabs-tab-content', dslcTabs);

	var dslcTabsNavVal = '';
	var dslcTabsContentVal = '';
	var dslcTabsNavValCount = 0;
	var dslcTabsContentValCount = 0;

	jQuery( '.dslc-tabs-nav-hook', dslcTabsNav ).each(function(){

		dslcTabsNavValCount++;

		if ( dslcTabsNavValCount > 1 ) {
			dslcTabsNavVal += ' (dslc_sep) ';
		}

		dslcTabsNavVal += jQuery(this).find('.dslc-tabs-nav-hook-title').text();	

	});

	dslcTabContent.each(function(){

		dslcTabsContentValCount++;

		if ( dslcTabsContentValCount > 1 ) {
			dslcTabsContentVal += ' (dslc_sep) ';
		}

		dslcTabsContentVal += jQuery(this).html();

	});

	jQuery('.dslca-module-option-front[data-id="tabs_nav"]', dslcTabsContainer).val( dslcTabsNavVal );
	jQuery('.dslca-module-option-front[data-id="tabs_content"]', dslcTabsContainer).val( dslcTabsContentVal );

	dslc_option_changed();

}

function dslc_accordion_generate_code( dslcAccordion ) {

	var dslcModule = dslcAccordion.closest('.dslc-module-front'),
	dslcAccordionCount = 0,
	dslcAccordionTitleVal = '',
	dslcAccordionContentVal = '';

	jQuery( '.dslc-accordion-item', dslcAccordion ).each(function(){

		dslcAccordionCount++;

		if ( dslcAccordionCount > 1 ) {
			dslcAccordionTitleVal += ' (dslc_sep) ';
			dslcAccordionContentVal += ' (dslc_sep) ';
		}

		dslcAccordionTitleVal += jQuery(this).find('.dslc-accordion-title').text();	
		dslcAccordionContentVal += jQuery(this).find('.dslc-accordion-content').html();	

	});

	jQuery('.dslca-module-option-front[data-id="accordion_nav"]', dslcModule).val( dslcAccordionTitleVal );
	jQuery('.dslca-module-option-front[data-id="accordion_content"]', dslcModule).val( dslcAccordionContentVal );

	dslc_option_changed();

}

function dslc_tabs() { 

	var dslcTabs, dslcTabsNav, dslcTabsContent, dslcTabContent;

	jQuery('.dslc-tabs').each(function(){

		dslcTabs = jQuery(this);
		dslcTabsNav = jQuery('.dslc-tabs-nav', dslcTabs);
		dslcTabsContent = jQuery('.dslc-tabs-content', dslcTabs);
		dslcTabContent = jQuery('.dslc-tabs-tab-content', dslcTabs);

		dslcTabContent.eq(0).addClass('dslc-active');
		jQuery('.dslc-tabs-nav-hook', dslcTabsNav ).eq(0).addClass('dslc-active');

	});

}

function dslc_download_count_increment( post_id ) {

	jQuery.post(

		DSLCAjax.ajaxurl,
		{
			action : 'dslc-download-count-increment',
			dslc_post_id : post_id
		},
		function( response ) { }

	);

}

jQuery(document).ready(function($){

	dslc_browser_classes();
	dslc_bg_video();

	/**
	 * Tabs
	 */

		dslc_tabs();
		dslc_init_square();
		dslc_center();

		/**
		 * Tabs
		 */

		jQuery(document).on( 'click', '.dslca-add-new-tab-hook', function(){

			var dslcTabs = jQuery(this).closest('.dslc-tabs'),
			dslcTabsNavLast = jQuery('.dslc-tabs-nav-hook:last', dslcTabs),
			dslcTabsContent = jQuery('.dslc-tabs-content', dslcTabs),
			dslcTabContentLast = jQuery('.dslc-tabs-tab-content:last', dslcTabs);

			dslcTabsNavLast.after('<span class="dslc-tabs-nav-hook"><span class="dslc-tabs-nav-hook-title" contenteditable>Click to edit title</span><span class="dslca-delete-tab-hook"><span class="dslca-icon dslc-icon-remove"></span></span></span>');
			dslcTabContentLast.after('<div class="dslc-tabs-tab-content" contenteditable>This is just placeholder text. Click here to edit it.</div>');

			jQuery('.dslc-tabs-nav-hook:last', dslcTabs).click();

			dslc_tabs_generate_code( dslcTabs );

			if ( ! jQuery(this).closest('.dslc-module-front').hasClass('dslca-module-being-edited') ) {
				jQuery(this).closest('.dslc-module-front').find('.dslca-module-edit-hook').trigger('click');
			}

		});

		jQuery(document).on( 'click', '.dslca-delete-tab-hook', function(e){

			var dslcTabs = jQuery(this).closest('.dslc-tabs');
			var dslcTabHook = jQuery(this).closest('.dslc-tabs-nav-hook');
			var dslcTabIndex = dslcTabHook.index();
			var dslcTabContent = jQuery('.dslc-tabs-tab-content', dslcTabs).eq( dslcTabIndex );

			if ( jQuery( '.dslc-tabs-nav-hook', dslcTabs ).length > 1 ) {

				dslcTabHook.remove();
				dslcTabContent.remove();

				if ( ! jQuery( '.dslc-tabs-tab-content.dslc-active', dslcTabs ).length ) {
					jQuery( '.dslc-tabs-nav-hook:first', dslcTabs ).trigger('click');
				}

				dslc_tabs_generate_code( dslcTabs );

			} else {

				alert( 'You can not delete the last remaining tab' );

			}

			e.stopPropagation()

		});

		jQuery(document).on( 'click', '.dslc-tabs-nav-hook', function(e){

			if ( ! jQuery(this).hasClass('dslc-active') ) {				

				dslcTabs = jQuery(this).closest('.dslc-tabs');
				dslcTabsNav = jQuery('.dslc-tabs-nav', dslcTabs);
				dslcTabsContent = jQuery('.dslc-tabs-content', dslcTabs);
				dslcTabContent = jQuery('.dslc-tabs-tab-content', dslcTabs);
				dslcTabIndex = jQuery(this).index();

				// Tabs nav
				jQuery('.dslc-tabs-nav-hook.dslc-active').removeClass('dslc-active');
				jQuery(this).addClass('dslc-active');

				// Tabs content

				if ( jQuery( '.dslc-tabs-tab-content.dslc-active', dslcTabs ).length ) {

					jQuery('.dslc-tabs-tab-content.dslc-active', dslcTabs).animate({
						opacity : 0
					}, 250, function(){
						jQuery(this).removeClass('dslc-active');
						dslcTabContent.eq(dslcTabIndex).css({ opacity : 0 }).addClass('dslc-active').show().animate({
							opacity : 1
						}, 250);
					});

				} else {
					dslcTabContent.eq(dslcTabIndex).css({ opacity : 0 }).addClass('dslc-active').show().animate({
						opacity : 1
					}, 250);
				}

			}

		});

		jQuery(document).on('blur paste', '.dslc-tabs-nav-hook-title[contenteditable], .dslc-tabs-tab-content[contenteditable]', function() {
			
			dslc_tabs_generate_code( jQuery(this).closest('.dslc-tabs') );

		}).on('focus', '.dslc-tabs-nav-hook-title[contenteditable], .dslc-tabs-tab-content[contenteditable]', function() {

			if ( ! jQuery(this).closest('.dslc-module-front').hasClass('dslca-module-being-edited') ) {
				jQuery(this).closest('.dslc-module-front').find('.dslca-module-edit-hook').trigger('click');
			}

		});


	// Close Notification
	$(document).on( 'click', '.dslc-notification-close', function(e){
		$(this).closest('.dslc-notification').slideUp(200, function(){
			$(this).remove();
		});
	});

	/**
	 * Filter
	 */

	$(document).on( 'click', '.dslc-post-filter', function(){

		// Get info
		var dslcCat = $(this).data('id');
		var dslcPosts = $(this).closest('.dslc-module-front').find('.dslc-post');
		var dslcFilterPosts = $(this).closest('.dslc-module-front').find('.dslc-post[data-cats*="' + dslcCat + '"]');
		var dslcNotFilterPosts = $(this).closest('.dslc-module-front').find('.dslc-post:not([data-cats*="' + dslcCat + '"])');
		var dslcContainer = dslcPosts.closest('.dslc-posts');
		var dslcWrapper = $(this).closest('.dslc-module-front');

		// Set active
		$(this).removeClass('dslc-inactive').addClass('dslc-active').siblings('.dslc-active').removeClass('dslc-active').addClass('dslc-inactive');

		if ( dslcContainer.hasClass('dslc-init-grid' ) ) {

			dslcFilterPosts.stop().animate({
				opacity : 1
			}, 300);

			dslcNotFilterPosts.stop().animate({
				opacity : 0.3
			}, 300);

		} else {

			// Hide posts
			
			dslcNotFilterPosts.removeClass('dslc-masonry-item dslc-masonry-item-animate').css({ visibility : 'hidden' });
			dslcFilterPosts.addClass('dslc-masonry-item dslc-masonry-item-animate').css({ visibility : 'visible' }).show();
			
			dslc_masonry( dslcWrapper, true );

		}

	});

	/**
	 * Download Count Hook
	 */

	$(document).on( 'click', '.dslc-download-count-hook', function(e) {

		dslc_download_count_increment( $(this).data('post-id') );

	});

	/**
	 * Notification Close
	 */

	$(document).on( 'click', '.dslc-notification-box-close', function() {
		$(this).closest('.dslc-notification-box').animate({
			opacity : 0
		}, 400, function(){
			$(this).remove();
		});
	});

	/**
	 * Lightbox
	 */

	dslc_init_lightbox();

	/**
	 * Animate Progress Bar
	 */

	$('.dslc-progress-bar-animated').each(function(){

		var dslcWrapper = $(this);
		var dslcEl = dslcWrapper.find('.dslc-progress-bar-loader-inner');
		var dslcVal = dslcEl.data('amount') + '%';

		dslcEl.css({ width : 0, opacity : 1 }).animate({ width : dslcVal }, 1000 );


	});

	/**
	 * Accordion
	 */

	dslc_init_accordion();

	$(document).on( 'click', '.dslc-accordion-hook', function(){

		var dslcActive = $(this).closest('.dslc-accordion-item'),
		dslcInactive = dslcActive.siblings('.dslc-accordion-item');

		dslcActive.removeClass('dslc-inactive').addClass('dslc-active');
		dslcInactive.removeClass('dslc-active').addClass('dslc-inactive');

		$('.dslc-accordion-content', dslcActive).slideDown(300);
		$('.dslc-accordion-content', dslcInactive).slideUp(300);

	});

	jQuery(document).on( 'click', '.dslca-add-accordion-hook', function(){

		var dslcAccordion = jQuery(this).closest('.dslc-accordion'),
		dslcAccordionLast = jQuery('.dslc-accordion-item:last', dslcAccordion),
		dslcAccordionNew = dslcAccordionLast.clone().insertAfter(dslcAccordionLast);

		jQuery('.dslc-accordion-title', dslcAccordionNew).html('CLICK TO EDIT');
		jQuery('.dslc-accordion-content', dslcAccordionNew).html('Placeholder content, click to edit. Lorem ipsum dolor sit amet, consectetur tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.');
		jQuery('.dslc-accordion-hook', dslcAccordionNew).click();

		dslc_accordion_generate_code( dslcAccordion );

		if ( ! jQuery(this).closest('.dslc-module-front').hasClass('dslca-module-being-edited') ) {
			jQuery(this).closest('.dslc-module-front').find('.dslca-module-edit-hook').trigger('click');
		}

	});

	jQuery(document).on( 'click', '.dslca-delete-accordion-hook', function(e){

		var dslcAccordion = jQuery(this).closest('.dslc-accordion'),
		dslcAccordionItem = jQuery(this).closest('.dslc-accordion-item');

		if ( ! jQuery(this).closest('.dslc-module-front').hasClass('dslca-module-being-edited') ) {
			jQuery(this).closest('.dslc-module-front').find('.dslca-module-edit-hook').trigger('click');
		}
		
		if ( jQuery( '.dslc-accordion-item', dslcAccordion ).length > 1 ) {

			dslcAccordionItem.remove();

			if ( ! jQuery( '.dslc-accordion-item.dslc-active', dslcAccordion ).length ) {
				jQuery( '.dslc-accordion-hook:first', dslcAccordion ).trigger('click');
			}

			dslc_accordion_generate_code( dslcAccordion );

		} else {

			alert( 'You can not delete the last remaining accordion item.' );

		}

		e.stopPropagation()

	});

	jQuery(document).on('blur paste keyup', '.dslc-accordion-title[contenteditable], .dslc-accordion-content[contenteditable]', function() {
		
		dslc_accordion_generate_code( jQuery(this).closest('.dslc-accordion') );

	}).on('focus', '.dslc-accordion-title[contenteditable], .dslc-accordion-content[contenteditable]', function() {

		if ( ! jQuery(this).closest('.dslc-module-front').hasClass('dslca-module-being-edited') ) {
			jQuery(this).closest('.dslc-module-front').find('.dslca-module-edit-hook').trigger('click');
		}

	});

	$(document).on( 'click', '.dslc-trigger-lightbox-gallery', function(e){

		e.preventDefault();

		jQuery(this).closest('.dslc-post').find('.dslc-lightbox-gallery a:first-child').trigger('click');

	});

});

jQuery(window).load(function(){

	dslc_carousel();
	dslc_masonry();
	dslc_parallax();
	dslc_init_square();
	dslc_center();
	dslc_responsive_classes();
	dslc_init_lightbox();

});

jQuery(window).resize(function(){

	dslc_center();
	dslc_responsive_classes();

});