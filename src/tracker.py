from flask import Flask, send_file, request, redirect
import io
import os
import sys
import base64

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import log_campaign_event

app = Flask(__name__)

# Transparent 1x1 GIF
PIXEL_DATA = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")

@app.route('/open/<tracking_id>')
def track_open(tracking_id):
    """
    Tracking pixel endpoint.
    tracking_id format: email_templateID_timestamp (base64 encoded ideally, or just raw for POC)
    For simplicity: email:template_id
    """
    try:
        # Simple parsing for POC
        if ":" in tracking_id:
            email, template_id = tracking_id.split(":", 1)
            log_campaign_event(email, "open", template_id=template_id, event_data=request.remote_addr)
            print(f"Tracked OPEN from {email}")
    except Exception as e:
        print(f"Tracking error: {e}")
        
    return send_file(io.BytesIO(PIXEL_DATA), mimetype='image/gif')

@app.route('/click/<tracking_id>')
def track_click(tracking_id):
    """
    Click tracking endpoint.
    Redirects to query param 'u'.
    """
    url = request.args.get('u', 'https://google.com')
    try:
        if ":" in tracking_id:
            email, template_id = tracking_id.split(":", 1)
            log_campaign_event(email, "click", template_id=template_id, event_data=url)
            print(f"Tracked CLICK from {email} -> {url}")
    except Exception as e:
        print(f"Tracking error: {e}")
        
    return redirect(url)

if __name__ == '__main__':
    print("Starting Tracking Server on port 5000...")
    app.run(host='0.0.0.0', port=5000)
