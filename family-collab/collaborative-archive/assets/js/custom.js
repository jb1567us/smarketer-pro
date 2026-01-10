(function($) {
    'use strict';

    // Collaborative Archive Theme JavaScript
    $(document).ready(function() {
        
        // Dashboard functionality
        function initDashboard() {
            // Auto-refresh collaboration tasks
            if ($('.collaboration-module').length) {
                setInterval(function() {
                    updateCollaborationTasks();
                }, 30000); // Update every 30 seconds
            }
            
            // Smooth scrolling for internal links
            $('a[href^="#"]').on('click', function(e) {
                e.preventDefault();
                var target = $(this.getAttribute('href'));
                if (target.length) {
                    $('html, body').animate({
                        scrollTop: target.offset().top - 80
                    }, 1000);
                }
            });
        }
        
        // Update collaboration tasks via AJAX
        function updateCollaborationTasks() {
            $.ajax({
                url: ca_ajax.ajax_url,
                type: 'POST',
                data: {
                    action: 'update_dashboard_modules',
                    module: 'collaboration_tasks',
                    nonce: ca_ajax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        // Update the tasks list
                        updateTasksList(response.data);
                    }
                }
            });
        }
        
        // Update the tasks list in the DOM
        function updateTasksList(tasks) {
            var $tasksList = $('.pending-list');
            if (tasks.length > 0) {
                var tasksHtml = '';
                tasks.forEach(function(task) {
                    tasksHtml += '<li><a href="' + task.link + '">' + task.title + '</a></li>';
                });
                $tasksList.html(tasksHtml);
            } else {
                $tasksList.html('<li>No pending tasks</li>');
            }
        }
        
        // Chapter status indicators
        function initChapterStatus() {
            $('.status-draft').each(function() {
                $(this).prepend('<span class="status-icon">📝 </span>');
            });
            
            $('.status-needs_review').each(function() {
                $(this).prepend('<span class="status-icon">👀 </span>');
            });
            
            $('.status-ready_to_publish').each(function() {
                $(this).prepend('<span class="status-icon">✅ </span>');
            });
            
            $('.status-published').each(function() {
                $(this).prepend('<span class="status-icon">📖 </span>');
            });
        }
        
        // Narrative arc tag interactions
        function initNarrativeArcs() {
            $('.arc-tag').on('click', function() {
                var arc = $(this).text().trim();
                var arcSlug = $(this).hasClass('arc-art-culture') ? 'art-culture' :
                             $(this).hasClass('arc-political-life') ? 'political-life' :
                             $(this).hasClass('arc-intelligence-file') ? 'intelligence-file' : '';
                
                if (arcSlug) {
                    window.location.href = '/narrative-arc/' + arcSlug + '/';
                }
            });
        }
        
        // Mobile menu toggle
        function initMobileMenu() {
            var $menu = $('.main-navigation .nav-menu');
            if ($(window).width() < 768) {
                if (!$('#mobile-menu-toggle').length) {
                    $('.main-navigation').prepend('<button id="mobile-menu-toggle" aria-label="Toggle menu">☰</button>');
                    $menu.hide();
                    
                    $('#mobile-menu-toggle').on('click', function() {
                        $menu.slideToggle();
                        $(this).toggleClass('active');
                    });
                }
            } else {
                $menu.show();
                $('#mobile-menu-toggle').remove();
            }
        }
        
        // Initialize all functionality
        initDashboard();
        initChapterStatus();
        initNarrativeArcs();
        initMobileMenu();
        
        // Handle window resize
        $(window).on('resize', initMobileMenu);
        
        // Add loading states to buttons
        $('.button').on('click', function() {
            var $button = $(this);
            if (!$button.hasClass('button-secondary')) {
                $button.addClass('loading').prop('disabled', true);
                setTimeout(function() {
                    $button.removeClass('loading').prop('disabled', false);
                }, 1000);
            }
        });
        
        // Enhance chapter cards with hover effects
        $('.chapter-card, .chapter-archive-card').on('mouseenter', function() {
            $(this).addClass('card-hover');
        }).on('mouseleave', function() {
            $(this).removeClass('card-hover');
        });
        
        // Print functionality for chapters
        $('.single-chapter').prepend('<button class="print-chapter button button-secondary" style="float: right;">Print Chapter</button>');
        
        $('.print-chapter').on('click', function() {
            window.print();
        });
        
    });

})(jQuery);