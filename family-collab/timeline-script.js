jQuery(document).ready(function($) {
    // Animation on scroll
    function animateOnScroll() {
        $('.timeline-event').each(function() {
            var elementTop = $(this).offset().top;
            var elementBottom = elementTop + $(this).outerHeight();
            var viewportTop = $(window).scrollTop();
            var viewportBottom = viewportTop + $(window).height();
            
            if (elementBottom > viewportTop && elementTop < viewportBottom) {
                $(this).addClass('animate-in');
            }
        });
    }
    
    // Initial check
    animateOnScroll();
    
    // Check on scroll
    $(window).scroll(function() {
        animateOnScroll();
    });
});