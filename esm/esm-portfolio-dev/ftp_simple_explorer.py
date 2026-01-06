#!/usr/bin/env python3
"""
Enhanced FTP Explorer - List all root files and directories
"""

import ftplib


def explore_ftp():
    host = "ftp.elliotspencermorgan.com"
    username = "admin@elliotspencermorgan.com"
    password = "!Meimeialibe4r"
    
    try:
        print("Connecting to FTP...")
        ftp = ftplib.FTP()
        ftp.connect(host, 21)
        ftp.login(username, password)
        print(f"✅ Connected: {ftp.getwelcome()}\n")
        
        # Get current directory
        pwd = ftp.pwd()
        print(f"Current directory: {pwd}\n")
        
        # List all items with details
        print("="*60)
        print("ROOT DIRECTORY LISTING (DETAILED)")
        print("="*60)
        items = []
        ftp.retrlines('LIST', items.append)
        
        for item in items:
            print(item)
        
        print("\n" + "="*60)
        print("ROOT DIRECTORY LISTING (NAMES ONLY)")
        print("="*60)
        names = []
        ftp.retrlines('NLST', names.append)
        
        for name in names:
            print(f"  {name}")
        
        # Try to change to common WordPress directories
        print("\n" + "="*60)
        print("TESTING COMMON PATHS")
        print("="*60)
        
        test_paths = [
            'public_html',
            'www',
            'httpdocs',
            'web',
            'html',
            'wordpress',
            'wp'
        ]
        
        for path in test_paths:
            try:
                ftp.cwd(f'/{path}')
                print(f"✅ /{path} exists!")
                
                # List contents
                contents = []
                ftp.retrlines('NLST', contents.append)
                print(f"   Contents ({len(contents)} items): {', '.join(contents[:10])}")
                
                # Check for WordPress
                wp_files = ['wp-config.php', 'wp-content', 'wp-admin']
                found = [f for f in wp_files if f in contents]
                if found:
                    print(f"   🎯 WordPress indicators found: {', '.join(found)}")
                
                ftp.cwd('/')  # Go back to root
            except Exception as e:
                print(f"❌ /{path} does not exist or not accessible")
        
        ftp.quit()
        print("\n✅ Exploration complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    explore_ftp()
