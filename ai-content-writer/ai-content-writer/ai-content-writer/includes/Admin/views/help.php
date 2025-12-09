<?php
/**
 * Help Page.
 *
 * @since 1.0.0
 * @package AIContentWriter/Admin
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

?>
<div class="wrap aicw-wrap aicw-settings">
	<div class="aicw__header">
		<h2 class="wp-heading-inline">
			<?php esc_html_e( 'Help', 'ai-content-writer' ); ?>
		</h2>
		<p><?php esc_html_e( 'The following information will help you generate API keys to use with the AI Content Writer plugin.', 'ai-content-writer' ); ?></p>
	</div>
	<hr class="wp-header-end">
	<div class="aicw__body">
		<div id="aicw-form">
			<div class="aicw-form__content">
				<h2><?php esc_html_e( 'Here\'s how you can generate Google Gemini API key:', 'ai-content-writer' ); ?></h2>
				<p><?php esc_html_e( 'Here\'s a step-by-step guide to obtaining a free API key for Google Gemini and using it in Google AI Studio:', 'ai-content-writer' ); ?></p>
				<ol>
					<li>
						<h4><?php esc_html_e( 'Visit the Google AI API KEY landing page', 'ai-content-writer' ); ?></h4>
						<a href="https://ai.google.dev/gemini-api/docs/api-key" target="_blank" class="button button-secondary"><?php esc_html_e( 'Google Cloud Platform', 'ai-content-writer' ); ?></a>
						<p><?php esc_html_e( 'Under section "Get a Gemini API key", click on the "Get  a Gemini API key in Google AI Studio" button.', 'ai-content-writer' ); ?></p>
					</li>
					<li>
						<h4><?php esc_html_e( 'Create Google Gemini API Key in Google AI Studio:', 'ai-content-writer' ); ?></h4>
						<p><?php esc_html_e( 'If you do previous step correctly, you will be redirected to Google AI Studio where you can create a new project and generate an API key or click on the bellow link to visit Google AI Studio directly.', 'ai-content-writer' ); ?></p>
						<a href="https://aistudio.google.com/app/apikey" target="_blank" class="button button-secondary"><?php esc_html_e( 'Google AI Studio/App/API Key', 'ai-content-writer' ); ?></a>
						<p><?php esc_html_e( 'Simply click on the "Create API Key" button to generate a new API key. While creating the API key, you may need to create a new project in Google AI Studio and enable the Gemini API. There are no charges for using the Gemini API if you chose the free module.', 'ai-content-writer' ); ?></p>
					</li>
					<li>
						<h4><?php esc_html_e( 'Copy the API Key', 'ai-content-writer' ); ?></h4>
						<p><?php esc_html_e( 'After creating the API key, copy the key and save it in a secure location. You also have the opportunity to get the API key later from that page. The list of API keys will be displayed in the Google AI Studio.', 'ai-content-writer' ); ?></p>
						<a href="https://aistudio.google.com/apikey" target="_blank" class="button button-secondary"><?php esc_html_e( 'List of API key\'s', 'ai-content-writer' ); ?></a>
					</li>
				</ol>
				<h2><?php esc_html_e( 'Important Notes:', 'ai-content-writer' ); ?></h2>
				<ul>
					<li><?php esc_html_e( 'Free Usage Limits: Be aware of the free usage limits for the Gemini API. Exceeding these limits may incur charges.', 'ai-content-writer' ); ?></li>
					<li><?php esc_html_e( 'API Usage: Refer to the Gemini API documentation for specific usage guidelines and best practices.', 'ai-content-writer' ); ?></li>
					<li><?php esc_html_e( 'Security: Handle your API key securely to prevent unauthorized access.', 'ai-content-writer' ); ?></li>
				</ul>
				<h2><?php esc_html_e( 'Additional Resources:', 'ai-content-writer' ); ?></h2>
				<ul>
					<li>
						<a href="https://gemini.google.com/app" target="_blank">
							<?php esc_html_e( 'Gemini APP', 'ai-content-writer' ); ?>
						</a>
					</li>
					<li>
						<a href="https://ai.google.dev/" target="_blank">
							<?php esc_html_e( 'Gemini API Documentation', 'ai-content-writer' ); ?>
						</a>
					</li>
					<li>
						<a href="https://cloud.google.com/generative-ai-studio" target="_blank">
							<?php esc_html_e( 'Generative Google AI Studio', 'ai-content-writer' ); ?>
						</a>
					</li>
				</ul>
				<p><?php esc_html_e( 'By following these steps, you can effectively utilize the Gemini API in your Google AI Studio projects. If you encounter any issues or have questions, refer to the official documentation or contact Google Cloud Platform support.', 'ai-content-writer' ); ?></p>

				<h2><?php esc_html_e( 'Here\'s how you can get ChatGPT OpenAI API key:', 'ai-content-writer' ); ?></h2>
				<p><?php esc_html_e( 'Here are the steps to create a ChatGPT OpenAI API key:', 'ai-content-writer' ); ?></p>
				<ol>
					<li>
						<h4><?php esc_html_e( 'Sign Up/Log In: Go to OpenAI.com and create an account or log in.', 'ai-content-writer' ); ?></h4>
						<a href="https://platform.openai.com/" target="_blank" class="button button-secondary"><?php esc_html_e( 'OpenAI Website', 'ai-content-writer' ); ?></a>
					</li>
					<li>
						<h4><?php esc_html_e( 'Access API Page: Navigate to the OpenAI API page form the profile dashboard.', 'ai-content-writer' ); ?></h4>
						<a href="https://platform.openai.com/settings/profile/user" target="_blank" class="button button-secondary"><?php esc_html_e( 'Profile => OpenAI API Keys Page', 'ai-content-writer' ); ?></a>
					</li>
					<li>
						<h4><?php esc_html_e( 'Generate API Key: Click "Create a new secret key" and copy the generated key (you won’t be able to see it again).', 'ai-content-writer' ); ?></h4>
						<p><?php esc_html_e( 'You can use this API key to generate content using the AI Content Writer plugin.', 'ai-content-writer' ); ?></p>
					</li>
					<li>
						<h4><?php esc_html_e( 'Monitor Usage & Costs: Keep track of your API usage and costs in the OpenAI dashboard.', 'ai-content-writer' ); ?></h4>
						<p><?php esc_html_e( 'You can monitor your API usage and costs in the OpenAI dashboard. This will help you manage your API usage and costs effectively.', 'ai-content-writer' ); ?></p>
						<a href="https://openai.com/api/pricing/" target="_blank" class="button button-secondary"><?php esc_html_e( 'OpenAI API Pricing', 'ai-content-writer' ); ?></a>
						<a href="https://platform.openai.com/api/usage" target="_blank" class="button button-secondary"><?php esc_html_e( 'OpenAI API Usage', 'ai-content-writer' ); ?></a>
					</li>
				</ol>

				<h2><?php esc_html_e( 'Here\'s how you can generate Pexels API key', 'ai-content-writer' ); ?></h2>
				<p><?php esc_html_e( 'Here are the steps to create a Pexels API key:', 'ai-content-writer' ); ?></p>
				<ol>
					<li>
						<h4><?php esc_html_e( 'Sign Up/Log In: Go to Pexels.com and create an account or log in.', 'ai-content-writer' ); ?></h4>
						<a href="https://www.pexels.com/api/" target="_blank" class="button button-secondary"><?php esc_html_e( 'Pexels Website', 'ai-content-writer' ); ?></a>
					</li>
					<li>
						<h4><?php esc_html_e( 'Access API Page: Navigate to the Pexels API page.', 'ai-content-writer' ); ?></h4>
						<a href="https://www.pexels.com/api/" target="_blank" class="button button-secondary"><?php esc_html_e( 'Request API Page', 'ai-content-writer' ); ?></a>
					</li>
					<li>
						<h4><?php esc_html_e( 'Request API Key: Click "Get Started" or "Request an API Key".', 'ai-content-writer' ); ?></h4>
						<p><?php esc_html_e( 'Fill out the form with your details and click on the "Request API Key" button. You will receive an email with your API key.', 'ai-content-writer' ); ?></p>
					</li>
					<li>
						<h4><?php esc_html_e( 'Get API Key: After approval, you\'ll receive your API key, visible on the dashboard.', 'ai-content-writer' ); ?></h4>
						<p><?php esc_html_e( 'Copy the API key and save it in a secure location. You can use this API key to generate thumbnail images for AI-generated content using the AI Content Writer plugin.', 'ai-content-writer' ); ?></p>
						<a href="https://www.pexels.com/api/" target="_blank" class="button button-secondary"><?php esc_html_e( 'Dashboard: Pexels API Key', 'ai-content-writer' ); ?></a>
					</li>
				</ol>
			</div>
			<div class="aicw-form__aside">
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2><?php esc_html_e( 'Support', 'ai-content-writer' ); ?></h2>
					</div>
					<div class="aicw-sidebar__body">
						<p><?php esc_html_e( 'If you need help, please contact us.', 'ai-content-writer' ); ?></p>
						<p>
							<a href="https://beautifulplugins.com/support" target="_blank" class="button button-secondary">
								<?php esc_html_e( 'Contact Support', 'ai-content-writer' ); ?>
							</a>
						</p>
					</div>
				</div>
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2><?php esc_html_e( 'Our Popular Plugins', 'ai-content-writer' ); ?></h2>
					</div>
					<div class="aicw-sidebar__body">
						<ul>
							<li>&rarr;
								<a href="https://wordpress.org/plugins/send-emails/" target="_blank">
									<?php esc_html_e( 'Send Emails – Newsletters, Automation & Email Marketing for WordPress', 'ai-content-writer' ); ?>
								</a>
							</li>
							<li>&rarr;
								<a href="https://wordpress.org/plugins/essential-elements/" target="_blank">
									<?php esc_html_e( 'Essential Elements for WordPress', 'ai-content-writer' ); ?>
								</a>
							</li>
							<li>&rarr;
								<a href="https://wordpress.org/plugins/advanced-shortcodes/" target="_blank">
									<?php esc_html_e( 'Shortcodes – Advanced Shortcode Manager', 'ai-content-writer' ); ?>
								</a>
							</li>
							<li>&rarr;
								<a href="https://wordpress.org/plugins/post-showcase/" target="_blank">
									<?php esc_html_e( 'Post Showcase', 'ai-content-writer' ); ?>
								</a>
							</li>
							<li>&rarr;
								<a href="https://wordpress.org/plugins/sms-manager/" target="_blank">
									<?php esc_html_e( 'SMS Manager – SMS Notifications for WooCommerce', 'ai-content-writer' ); ?>
								</a>
							</li>
							<li>&rarr;
								<a href="https://wordpress.org/plugins/invoice-payment/" target="_blank">
									<?php esc_html_e( 'Invoice Payment', 'ai-content-writer' ); ?>
								</a>
							</li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
<?php
