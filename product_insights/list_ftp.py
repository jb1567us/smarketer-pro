import ftplib

FTP_HOST = "ftp.lookoverhere.xyz"
FTP_USER = "lookoverhere"
FTP_PASS = "!Meimeialibe4r"

try:
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("Login successful.")
    
    print("\nRoot Directory Listing:")
    ftp.dir()
    
    ftp.quit()
except Exception as e:
    print(f"Error: {e}")
