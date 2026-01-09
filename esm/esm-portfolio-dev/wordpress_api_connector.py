#!/usr/bin/env python3
"""
WordPress API Connector for Elliot Spencer Morgan Website
Tests connection and prepares for deployment
"""

import requests
import json
from base64 import b64encode


class WordPressAPI:
    """WordPress REST API client"""
    
    def __init__(self, site_url, username, password):
        """
        Initialize WordPress API client
        
        Args:
            site_url: WordPress site URL (e.g., https://elliotspencermorgan.com)
            username: WordPress admin username
            password: WordPress admin password
        """
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.username = username
        self.password = password
        
        # Create auth header
        credentials = f"{username}:{password}"
        token = b64encode(credentials.encode()).decode('utf-8')
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test WordPress API connection"""
        print("="*60)
        print("TESTING WORDPRESS API CONNECTION")
        print("="*60)
        print(f"\nSite URL: {self.site_url}")
        print(f"API URL: {self.api_url}")
        print(f"Username: {self.username}")
        
        try:
            # Test basic API access
            print("\n1. Testing basic API access...")
            response = requests.get(f"{self.site_url}/wp-json")
            if response.status_code == 200:
                print("   ✅ WordPress API is accessible")
                data = response.json()
                print(f"   Site name: {data.get('name', 'Unknown')}")
                print(f"   Description: {data.get('description', 'Unknown')}")
            else:
                print(f"   ❌ API not accessible: {response.status_code}")
                return False
            
            # Test authentication
            print("\n2. Testing authentication...")
            response = requests.get(
                f"{self.api_url}/users/me",
                headers=self.headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Display name: {user_data.get('name')}")
                print(f"   Roles: {', '.join(user_data.get('roles', []))}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return False
    
    def get_site_info(self):
        """Get WordPress site information"""
        print("\n" + "="*60)
        print("SITE INFORMATION")
        print("="*60)
        
        try:
            # Get site settings
            response = requests.get(
                f"{self.api_url}/settings",
                headers=self.headers
            )
            
            if response.status_code == 200:
                settings = response.json()
                print(f"\nTitle: {settings.get('title')}")
                print(f"Tagline: {settings.get('description')}")
                print(f"URL: {settings.get('url')}")
                print(f"Language: {settings.get('language')}")
                print(f"Timezone: {settings.get('timezone_string')}")
                return settings
            else:
                print(f"Could not retrieve settings: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting site info: {e}")
            return None
    
    def list_pages(self, per_page=10):
        """List existing pages"""
        print("\n" + "="*60)
        print(f"EXISTING PAGES (showing first {per_page})")
        print("="*60)
        
        try:
            response = requests.get(
                f"{self.api_url}/pages",
                headers=self.headers,
                params={'per_page': per_page, 'orderby': 'modified', 'order': 'desc'}
            )
            
            if response.status_code == 200:
                pages = response.json()
                print(f"\nTotal pages found: {len(pages)}")
                
                for page in pages:
                    print(f"\n  - {page['title']['rendered']}")
                    print(f"    ID: {page['id']}")
                    print(f"    Slug: {page['slug']}")
                    print(f"    Status: {page['status']}")
                    print(f"    Modified: {page['modified']}")
                
                return pages
            else:
                print(f"Could not retrieve pages: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error listing pages: {e}")
            return []
    
    def list_media(self, per_page=10):
        """List media files"""
        print("\n" + "="*60)
        print(f"MEDIA LIBRARY (showing first {per_page})")
        print("="*60)
        
        try:
            response = requests.get(
                f"{self.api_url}/media",
                headers=self.headers,
                params={'per_page': per_page, 'orderby': 'date', 'order': 'desc'}
            )
            
            if response.status_code == 200:
                media = response.json()
                print(f"\nTotal media items found: {len(media)}")
                
                for item in media:
                    print(f"\n  - {item['title']['rendered']}")
                    print(f"    ID: {item['id']}")
                    print(f"    Type: {item['mime_type']}")
                    print(f"    URL: {item['source_url']}")
                
                return media
            else:
                print(f"Could not retrieve media: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error listing media: {e}")
            return []
    
    def check_plugins(self):
        """Check installed plugins (requires authentication)"""
        print("\n" + "="*60)
        print("CHECKING PLUGINS")
        print("="*60)
        
        try:
            # Note: Plugin endpoint requires special permissions
            response = requests.get(
                f"{self.site_url}/wp-json/wp/v2/plugins",
                headers=self.headers
            )
            
            if response.status_code == 200:
                plugins = response.json()
                print(f"\nInstalled plugins: {len(plugins)}")
                for plugin in plugins:
                    status = "✅ Active" if plugin.get('status') == 'active' else "⭕ Inactive"
                    print(f"  {status} {plugin.get('name')}")
                return plugins
            else:
                print(f"Could not retrieve plugins (may require additional permissions)")
                return []
        except Exception as e:
            print(f"Plugin check not available: {e}")
            return []


def main():
    """Test WordPress API connection"""
    site_url = "https://elliotspencermorgan.com"
    username = "admin"
    password = "!Meimeialibe4r"
    
    api = WordPressAPI(site_url, username, password)
    
    # Test connection
    if api.test_connection():
        print("\n✅ WordPress API connection successful!")
        
        # Get site info
        api.get_site_info()
        
        # List pages
        api.list_pages(per_page=5)
        
        # List media
        api.list_media(per_page=5)
        
        # Check plugins
        api.check_plugins()
        
        print("\n" + "="*60)
        print("CONNECTION TEST COMPLETE")
        print("="*60)
        print("\n✅ Ready to deploy artwork pages!")
        print("\nNext steps:")
        print("1. Run artwork page generator")
        print("2. Upload optimized images")
        print("3. Create pages with VisualArtwork schema")
        print("4. Create collection pages")
        print("5. Update About/Contact pages")
        
    else:
        print("\n❌ WordPress API connection failed")
        print("\nPlease check:")
        print("- Site URL is correct")
        print("- Username and password are correct")
        print("- WordPress REST API is enabled")


if __name__ == "__main__":
    main()
