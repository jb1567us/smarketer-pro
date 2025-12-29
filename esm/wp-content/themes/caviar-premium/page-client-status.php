<?php
/**
 * Template Name: Client Status Page
 * Description: A template for displaying project status updates to clients.
 */

get_header(); ?>

<style>
    .status-page-container {
        max-width: 900px;
        margin: 40px auto;
        padding: 0 20px;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #333;
    }

    .status-header {
        border-bottom: 2px solid #eee;
        padding-bottom: 20px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }

    .status-title {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
    }

    .status-date {
        color: #7f8c8d;
        font-size: 1.1rem;
    }

    .status-indicator {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-green { background-color: #2ecc71; color: white; }
    .status-yellow { background-color: #f1c40f; color: #fff; text-shadow: 0 1px 1px rgba(0,0,0,0.1); }
    .status-red { background-color: #e74c3c; color: white; }

    .status-section {
        background: #fff;
        border: 1px solid #e1e8ed;
        border-radius: 8px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .status-section h2 {
        margin-top: 0;
        font-size: 1.5rem;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 15px;
        color: #34495e;
    }

    .status-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .status-list li {
        padding: 8px 0;
        display: flex;
        align-items: flex-start;
        line-height: 1.5;
    }

    .status-list li:before {
        content: '•';
        color: #3498db;
        font-weight: bold;
        display: inline-block; 
        width: 1em;
        margin-right: 5px;
    }
    
    .status-list.done li:before { content: '✓'; color: #2ecc71; }
    .status-list.todo li:before { content: '○'; color: #95a5a6; }
    .status-list.wip li:before { content: '▶'; color: #3498db; }
    
    .timeline {
        position: relative;
        padding-left: 20px;
        border-left: 2px solid #eee;
        margin-left: 10px;
    }
    
    .timeline-item {
        position: relative;
        margin-bottom: 20px;
        padding-left: 15px;
    }
    
    .timeline-item:before {
        content: '';
        position: absolute;
        left: -26px;
        top: 5px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #bdc3c7;
        border: 2px solid #fff;
    }
    
    .timeline-item.completed:before { background: #2ecc71; }
    .timeline-item.current:before { background: #3498db; }
    
    .timeline-date {
        font-size: 0.85rem;
        color: #7f8c8d;
        margin-bottom: 3px;
    }
    
    .timeline-title {
        font-weight: 600;
        color: #2c3e50;
    }

    /* Responsive adjustments */
    @media (max-width: 600px) {
        .status-header {
            flex-direction: column;
            align-items: flex-start;
        }
    }

    /* Dashboard Specific Styles */
    :root {
        --bg: #111;
        --card-bg: #1a1a1a;
        --text: #eee;
        --text-muted: #aaa;
        --accent: #d4af37; /* Gold */
        --accent-dim: #8a7020;
        --success: #4caf50;
        --progress-bg: #333;
    }
    /* Note: body background override removed to respect theme context, 
       but container inside can use dark mode */
    
    .status-content .container {
        /* max-width: 900px; margin: 0 auto; - already in container class but scoped */
    }
    
    /* Scoped Dark Mode for Dashboard Content */
    .status-content {
        background: var(--bg);
        color: var(--text);
        padding: 20px;
        border-radius: 8px;
    }

    .status-content h1 {
        font-weight: 300;
        letter-spacing: -1px;
        margin: 0 0 10px 0;
        font-size: 2.5rem;
        color: var(--text);
    }
    
    .meta {
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .global-progress {
        background: var(--card-bg);
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #333;
        color: var(--text);
    }
    .stat-box h3 { margin: 0; font-size: 3rem; color: var(--accent); font-weight: 300; }
    .stat-box p { margin: 0; color: var(--text-muted); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }
    
    .phase-card {
        background: var(--card-bg);
        border-radius: 8px;
        margin-bottom: 30px;
        overflow: hidden;
        border: 1px solid #333;
        color: var(--text);
    }
    .phase-header {
        padding: 20px 30px;
        background: #222;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
    }
    .phase-header h2 { margin: 0; font-size: 1.2rem; font-weight: 500; color: var(--text); }
    .phase-meta { color: var(--text-muted); font-size: 0.9rem; }
    
    .progress-bar-container {
        height: 4px;
        background: var(--progress-bg);
        width: 100%;
    }
    .progress-bar-fill {
        height: 100%;
        background: var(--accent);
        transition: width 0.3s ease;
    }
    
    .task-list {
        padding: 20px 30px;
    }
    .task-item {
        padding: 8px 0;
        display: flex;
        align-items: flex-start;
        border-bottom: 1px solid #2a2a2a;
    }
    .task-item:last-child { border-bottom: none; }
    .status-icon {
        margin-right: 15px;
        font-size: 1.1rem;
        width: 20px;
        text-align: center;
    }
    .status-done { color: var(--success); }
    .status-inprogress { color: var(--accent); }
    .status-todo { color: #444; }
    
    .task-text { font-size: 0.95rem; }
    .task-done .task-text { color: var(--text-muted); text-decoration: line-through; opacity: 0.6; }
    
    @media (max-width: 600px) {
        .global-progress { flex-direction: column; text-align: center; gap: 20px; }
        .status-content h1 { font-size: 1.8rem; }
    }
</style>

<div class="status-page-container">
    
    <!-- Header Section -->
    <header class="status-header">
        <div>
            <h1 class="status-title"><?php the_title(); ?></h1>
            <div class="status-date">Last Updated: <?php echo get_the_modified_date('F j, Y'); ?></div>
        </div>
        <!-- 
            Example Status Pill:
            Change class to status-green, status-yellow, or status-red
        -->
        <div class="status-indicator status-green">
            Project Status: On Track
        </div>
    </header>
    
    <?php 
    // Start the Loop.
    while ( have_posts() ) : the_post(); 
    ?>
    
    <div class="status-content">
        <!-- 
           The WordPress Editor Content 
           Allows the client to add custom text, images, or updates via the CMS 
        -->
        <?php the_content(); ?>
    </div>
    
    <?php endwhile; ?>

    <!-- Example Structure for Hardcoded Sections (Optional) -->
    <!-- Ideally, users would build this in the Block Editor, but here are semantic wrappers if needed -->
    
    <!-- 
    <div class="status-section">
        <h2>🚀 Recent Accomplishments</h2>
        <ul class="status-list done">
            <li>Completed homepage redesign</li>
            <li>Fixed mobile navigation bug</li>
            <li>Optimized images for faster load time</li>
        </ul>
    </div>

    <div class="status-section">
        <h2>🚧 Work in Progress</h2>
        <ul class="status-list wip">
            <li>Integrating payment gateway</li>
            <li>Writing documentation</li>
        </ul>
    </div>

    <div class="status-section">
        <h2>📅 Upcoming Milestones</h2>
        <div class="timeline">
            <div class="timeline-item completed">
                <div class="timeline-date">Oct 15, 2023</div>
                <div class="timeline-title">Project Kickoff</div>
            </div>
            <div class="timeline-item current">
                <div class="timeline-date">Nov 1, 2023</div>
                <div class="timeline-title">Alpha Release</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-date">Nov 15, 2023</div>
                <div class="timeline-title">Beta Testing</div>
            </div>
        </div>
    </div>
    -->

</div>

<?php get_footer(); ?>
