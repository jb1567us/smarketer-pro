#!/usr/bin/env python3
"""
FTP Site Explorer for Elliot Spencer Morgan Website
Connects to hosting and maps the WordPress structure
"""

import ftplib
import os
from pathlib import Path
import json
from datetime import datetime


class SiteExplorer:
    """Explore WordPress site via FTP"""
    
    def __init__(self, host, username, password, port=21):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ftp = None
    
    def connect(self):
        """Connect to FTP server"""
        try:
            print(f"Connecting to {self.host}...")
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
            print(f"✅ Connected successfully!")
            print(f"Welcome message: {self.ftp.getwelcome()}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def explore_structure(self, max_depth=3):
        """Explore directory structure"""
        if not self.ftp:
            print("Not connected!")
            return
        
        print("\n" + "="*60)
        print("EXPLORING SITE STRUCTURE")
        print("="*60)
        
        # Get current directory
        current_dir = self.ftp.pwd()
        print(f"\nCurrent directory: {current_dir}")
        
        # List root contents
        print("\nRoot directory contents:")
        structure = {}
        self._explore_dir("/", structure, current_depth=0, max_depth=max_depth)
        
        # Save structure
        output_file = "site_structure.json"
        with open(output_file, 'w') as f:
            json.dump(structure, f, indent=2)
        print(f"\n✅ Site structure saved to {output_file}")
        
        return structure
    
    def _explore_dir(self, path, structure, current_depth=0, max_depth=3):
        """Recursively explore directory"""
        if current_depth >= max_depth:
            return
        
        try:
            items = []
            self.ftp.cwd(path)
            self.ftp.retrlines('LIST', items.append)
            
            dirs = []
            files = []
            
            for item in items:
                parts = item.split()
                if len(parts) < 9:
                    continue
                
                permissions = parts[0]
                name = ' '.join(parts[8:])
                
                # Skip . and ..
                if name in ['.', '..']:
                    continue
                
                is_dir = permissions.startswith('d')
                
                if is_dir:
                    dirs.append(name)
                    print(f"{'  ' * current_depth}📁 {name}/")
                else:
                    files.append(name)
                    if current_depth < 2:  # Only show files at shallow depth
                        print(f"{'  ' * current_depth}📄 {name}")
            
            structure[path] = {
                'directories': dirs,
                'files': files,
                'file_count': len(files),
                'dir_count': len(dirs)
            }
            
            # Recurse into subdirectories
            for dir_name in dirs:
                # Skip common large/unimportant directories
                if dir_name in ['node_modules', '.git', 'cache', 'logs']:
                    continue
                
                subpath = f"{path.rstrip('/')}/{dir_name}"
                self._explore_dir(subpath, structure, current_depth + 1, max_depth)
        
        except Exception as e:
            print(f"{'  ' * current_depth}⚠️  Error exploring {path}: {e}")
    
    def find_wordpress_root(self):
        """Find WordPress installation directory"""
        print("\n" + "="*60)
        print("FINDING WORDPRESS INSTALLATION")
        print("="*60)
        
        # Common WordPress locations
        common_paths = [
            "/",
            "/public_html",
            "/www",
            "/httpdocs",
            "/web",
            "/html"
        ]
        
        for path in common_paths:
            try:
                self.ftp.cwd(path)
                items = []
                self.ftp.retrlines('NLST', items.append)
                
                # Check for WordPress indicators
                wp_indicators = ['wp-config.php', 'wp-content', 'wp-admin', 'wp-includes']
                found_indicators = [ind for ind in wp_indicators if ind in items]
                
                if len(found_indicators) >= 3:
                    print(f"\n✅ WordPress found at: {path}")
                    print(f"   Indicators: {', '.join(found_indicators)}")
                    return path
            except:
                continue
        
        print("\n⚠️  WordPress root not found in common locations")
        return None
    
    def check_wordpress_version(self, wp_root):
        """Check WordPress version"""
        try:
            version_file = f"{wp_root}/wp-includes/version.php"
            self.ftp.cwd(wp_root + "/wp-includes")
            
            # Download version.php to temp
            temp_file = "temp_version.php"
            with open(temp_file, 'wb') as f:
                self.ftp.retrbinary(f'RETR version.php', f.write)
            
            # Read version
            with open(temp_file, 'r') as f:
                content = f.read()
                import re
                match = re.search(r"\$wp_version\s*=\s*'([^']+)'", content)
                if match:
                    version = match.group(1)
                    print(f"\n✅ WordPress version: {version}")
                    os.remove(temp_file)
                    return version
            
            os.remove(temp_file)
        except Exception as e:
            print(f"⚠️  Could not determine WordPress version: {e}")
        
        return None
    
    def list_themes(self, wp_root):
        """List installed themes"""
        try:
            themes_path = f"{wp_root}/wp-content/themes"
            self.ftp.cwd(themes_path)
            themes = []
            self.ftp.retrlines('NLST', themes.append)
            
            print(f"\n📦 Installed themes:")
            for theme in themes:
                if theme not in ['.', '..']:
                    print(f"   - {theme}")
            
            return themes
        except Exception as e:
            print(f"⚠️  Could not list themes: {e}")
            return []
    
    def list_plugins(self, wp_root):
        """List installed plugins"""
        try:
            plugins_path = f"{wp_root}/wp-content/plugins"
            self.ftp.cwd(plugins_path)
            plugins = []
            self.ftp.retrlines('NLST', plugins.append)
            
            print(f"\n🔌 Installed plugins:")
            for plugin in plugins:
                if plugin not in ['.', '..']:
                    print(f"   - {plugin}")
            
            return plugins
        except Exception as e:
            print(f"⚠️  Could not list plugins: {e}")
            return []
    
    def disconnect(self):
        """Close FTP connection"""
        if self.ftp:
            self.ftp.quit()
            print("\n✅ Disconnected from FTP")


def main():
    """Main exploration script"""
    # FTP credentials
    host = "ftp.elliotspencermorgan.com"
    username = "admin@elliotspencermorgan.com"
    password = "!Meimeialibe4r"
    
    explorer = SiteExplorer(host, username, password)
    
    if explorer.connect():
        # Find WordPress
        wp_root = explorer.find_wordpress_root()
        
        if wp_root:
            # Get WordPress info
            explorer.check_wordpress_version(wp_root)
            explorer.list_themes(wp_root)
            explorer.list_plugins(wp_root)
        
        # Explore structure
        explorer.explore_structure(max_depth=2)
        
        explorer.disconnect()
        
        print("\n" + "="*60)
        print("EXPLORATION COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Review site_structure.json")
        print("2. Identify WordPress root directory")
        print("3. Plan deployment strategy")
    else:
        print("\n❌ Could not connect to FTP server")


if __name__ == "__main__":
    main()
