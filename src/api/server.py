"""
REST API for B2B Outreach Tool
Provides programmatic access to leads, campaigns, and enrichment functions.
"""
from flask import Flask, request, jsonify
from functools import wraps
import secrets
from database import (
    load_data, save_data, get_all_campaigns, 
    add_lead_to_campaign, get_connection
)
import sqlite3

app = Flask(__name__)

# Simple API key storage (in production, use database)
API_KEYS = {}

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        if api_key not in API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ============= API Key Management =============

@app.route('/api/v1/keys', methods=['POST'])
def create_api_key():
    """Create a new API key."""
    # In production, add admin authentication here
    key = generate_api_key()
    name = request.json.get('name', 'Unnamed Key')
    API_KEYS[key] = {'name': name, 'created_at': 'now'}
    
    return jsonify({
        'api_key': key,
        'name': name,
        'message': 'Store this key securely - it cannot be retrieved later'
    }), 201

# ============= Lead Endpoints =============

@app.route('/api/v1/leads', methods=['GET'])
@require_api_key
def get_leads():
    """Get all leads with optional filtering."""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    source = request.args.get('source')
    
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        query = "SELECT * FROM leads"
        params = []
        
        if source:
            query += " WHERE source = ?"
            params.append(source)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        c.execute(query, params)
        leads = [dict(row) for row in c.fetchall()]
        
        return jsonify({
            'leads': leads,
            'count': len(leads),
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/v1/leads/<int:lead_id>', methods=['GET'])
@require_api_key
def get_lead(lead_id):
    """Get a specific lead by ID."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        lead = c.fetchone()
        
        if not lead:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify(dict(lead)), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/v1/leads', methods=['POST'])
@require_api_key
def create_lead():
    """Create a new lead."""
    data = request.json
    
    required_fields = ['url']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: url'}), 400
    
    try:
        # Add lead to database
        lead_data = [{
            'url': data['url'],
            'emails': data.get('emails', []),
            'details': data.get('details', {}),
            'source': data.get('source', 'api'),
            'analysis': data.get('analysis', {})
        }]
        
        save_data(lead_data)
        
        return jsonify({
            'message': 'Lead created successfully',
            'lead': lead_data[0]
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/leads/<int:lead_id>', methods=['PUT'])
@require_api_key
def update_lead(lead_id):
    """Update a lead."""
    data = request.json
    
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Build update query dynamically
        update_fields = []
        params = []
        
        for field in ['url', 'emails', 'details', 'source', 'analysis']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(str(data[field]))
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(lead_id)
        query = f"UPDATE leads SET {', '.join(update_fields)} WHERE id = ?"
        
        c.execute(query, params)
        conn.commit()
        
        if c.rowcount == 0:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify({'message': 'Lead updated successfully'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/v1/leads/<int:lead_id>', methods=['DELETE'])
@require_api_key
def delete_lead(lead_id):
    """Delete a lead."""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        
        if c.rowcount == 0:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify({'message': 'Lead deleted successfully'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ============= Campaign Endpoints =============

@app.route('/api/v1/campaigns', methods=['GET'])
@require_api_key
def get_campaigns():
    """Get all campaigns."""
    campaigns = get_all_campaigns()
    return jsonify({'campaigns': campaigns}), 200

@app.route('/api/v1/campaigns/<int:campaign_id>/leads', methods=['POST'])
@require_api_key
def add_lead_to_campaign_endpoint(campaign_id):
    """Add a lead to a campaign."""
    data = request.json
    lead_id = data.get('lead_id')
    
    if not lead_id:
        return jsonify({'error': 'lead_id required'}), 400
    
    try:
        success = add_lead_to_campaign(campaign_id, lead_id)
        
        if success:
            return jsonify({'message': 'Lead added to campaign'}), 200
        else:
            return jsonify({'error': 'Failed to add lead to campaign'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= Enrichment Endpoint =============

@app.route('/api/v1/enrich', methods=['POST'])
@require_api_key
def trigger_enrichment():
    """Trigger enrichment for a lead."""
    data = request.json
    lead_id = data.get('lead_id')
    
    if not lead_id:
        return jsonify({'error': 'lead_id required'}), 400
    
    # This would trigger async enrichment
    # For now, return queued status
    return jsonify({
        'message': 'Enrichment queued',
        'lead_id': lead_id,
        'status': 'queued'
    }), 202

# ============= Health Check =============

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    # Generate initial API key for testing
    initial_key = generate_api_key()
    API_KEYS[initial_key] = {'name': 'Initial Key', 'created_at': 'now'}
    print(f"Initial API Key: {initial_key}")
    print("Store this securely!")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
