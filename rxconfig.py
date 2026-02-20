import reflex as rx

config = rx.Config(
    app_name="b2b_outreach_proto",
    db_url="sqlite:///reflex.db",
    state_auto_setters=True,
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
