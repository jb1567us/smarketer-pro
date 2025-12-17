import typer
from rich.console import Console
from rich.table import Table
from .config import Config
from .client import CPanelClient
from .wp import WordPressManager
from .maintenance import MaintenanceManager
from .browser_bot import BrowserBot
from .file_manager import FileManager

app = typer.Typer(help="cPanel Shared Hosting Automation Tool")
console = Console()

def get_client():
    try:
        config = Config()
        config.validate()
        return CPanelClient(config)
    except Exception as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print("Please ensure config.yaml or ENV vars are set correctly.")
        raise typer.Exit(code=1)

@app.command()
def status():
    """Show general hosting account status (Domains, Disk Usage)."""
    client = get_client()
    maintenance = MaintenanceManager(client)
    
    with console.status("Fetching data..."):
        try:
            domains = client.list_domains()
            alerts = maintenance.check_disk_usage()
            
            # Show Domains
            table = Table(title="Domains")
            table.add_column("Domain", style="cyan")
            table.add_column("Root", style="green")
            for d in domains:
                table.add_row(d.get("domain"), d.get("documentroot"))
            console.print(table)
            
            # Show Alerts
            if alerts:
                console.print("\n[bold red]Warnings:[/bold red]")
                for a in alerts:
                    console.print(f"- {a}")
            else:
                console.print("\n[bold green]Storage is healthy.[/bold green]")

        except Exception as e:
            console.print(f"[red]Error fetching status:[/red] {e}")

@app.command()
def wp_list():
    """List all WordPress installations."""
    client = get_client()
    mgr = WordPressManager(client)
    
    try:
        sites = mgr.list_sites()
        if not sites:
            console.print("No WordPress sites found (or WP Toolkit not active).")
            return

        table = Table(title="WordPress Sites")
        table.add_column("URL", style="cyan")
        table.add_column("Version", style="magenta")
        table.add_column("Update Status", style="green")
        
        for s in sites:
            # Note: Fields depend on WPToolkit return data
            table.add_row(
                s.get("full_url", "N/A"),
                s.get("version", "Unknown"),
                s.get("update_status", "Unknown") 
            )
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

@app.command()
def backup():
    """Trigger a full account backup to home directory."""
    client = get_client()
    mgr = MaintenanceManager(client)
    
    if typer.confirm("This will start a full backup process. It may take some time. Continue?"):
        try:
            mgr.trigger_full_backup()
            console.print("[green]Backup process started successfully![/green]")
        except Exception as e:
            console.print(f"[red]Backup failed:[/red] {e}")

@app.command()
def backup_browser(headless: bool = False):
    """
    Trigger a full backup using Browser Automation (Playwright).
    Useful if API access is restricted.
    """
    # Force validate for password for this specific command
    try:
        config = Config()
        if not config.cpanel_password:
             console.print("[bold red]Error:[/bold red] CPANEL_PASSWORD is required for browser mode.")
             raise typer.Exit(code=1)
        
        bot = BrowserBot(config, headless=headless)
        console.print("[yellow]Launching browser to perform backup...[/yellow]")
        bot.run_backup()
        
    except Exception as e:
        console.print(f"[red]Browser Automation Error:[/red] {e}")

@app.command()
def files_list(path: str = "public_html"):
    """List files in a directory (API Mode)."""
    client = get_client()
    mgr = FileManager(client)
    
    try:
        files = mgr.list_files(path)
        table = Table(title=f"Files in {path}")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Type", style="magenta")
        
        for f in files:
            table.add_row(
                f.get("file"),
                f.get("size"),
                f.get("type")
            )
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing files:[/red] {e}")

@app.command()
def files_browse():
    """
    Open File Manager in a visible browser window.
    """
    try:
        config = Config()
        if not config.cpanel_password:
             console.print("[bold red]Error:[/bold red] CPANEL_PASSWORD is required.")
             raise typer.Exit(code=1)
        
        # Always run visible for this interaction
        bot = BrowserBot(config, headless=False)
        bot.open_file_manager()
        
        bot.open_file_manager()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

@app.command()
def files_upload(local_path: str, remote_dir: str = "public_html"):
    """Upload a local file to the server."""
    client = get_client()
    mgr = FileManager(client)
    try:
        console.print(f"Uploading [bold]{local_path}[/bold] to [bold]{remote_dir}[/bold]...")
        mgr.upload_file(local_path, remote_dir)
        console.print("[green]Upload successful![/green]")
    except Exception as e:
        console.print(f"[red]Upload failed:[/red] {e}")

@app.command()
def files_upload_browser(local_path: str, remote_path: str, headless: bool = False):
    """
    Upload a file using Browser Automation.
    remote_path: e.g. public_html/test.php
    """
    try:
        config = Config()
        if not config.cpanel_password:
             console.print("[bold red]Error:[/bold red] CPANEL_PASSWORD is required.")
             raise typer.Exit(code=1)
        
        bot = BrowserBot(config, headless=headless)
        console.print(f"[yellow]Uploading {local_path} to {remote_path}...[/yellow]")
        bot.upload_file(local_path, remote_path)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

@app.command()
def files_delete(remote_path: str):
    """Delete a remote file (Permanent)."""
    client = get_client()
    mgr = FileManager(client)
    if typer.confirm(f"Are you sure you want to PERMANENTLY delete '{remote_path}'?"):
        try:
            mgr.delete_file(remote_path)
            console.print("[green]File deleted.[/green]")
        except Exception as e:
             console.print(f"[red]Delete failed:[/red] {e}")

@app.command()
def files_mkdir(parent: str, name: str):
    """Create a new directory."""
    client = get_client()
    mgr = FileManager(client)
    try:
        mgr.create_directory(parent, name)
        console.print(f"[green]Directory '{name}' created in '{parent}'.[/green]")
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")

@app.command()
def files_cat(remote_path: str):
    """View file content (Text files)."""
    client = get_client()
    mgr = FileManager(client)
    try:
        res = mgr.get_file_content(remote_path)
        # UAPI often returns dict { content: ..., encoding: ... }
        content = res.get("content") if isinstance(res, dict) else res
        print(content)
    except Exception as e:
         console.print(f"[red]Error:[/red] {e}")

@app.command()
def files_download(remote_path: str, local_path: str):
    """Download a remote file to local machine."""
    client = get_client()
    mgr = FileManager(client)
    try:
        console.print(f"Downloading [bold]{remote_path}[/bold]...")
        mgr.download_file(remote_path, local_path)
        console.print(f"[green]Saved to {local_path}[/green]")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[red]Download failed:[/red] {e}")

@app.command()
def files_compress(sources: str, dest: str, type: str = "zip"):
    """
    Compress files/folders. 
    Usage: files-compress "folder1,file2.txt" public_html/archive.zip
    """
    client = get_client()
    mgr = FileManager(client)
    try:
        source_list = [s.strip() for s in sources.split(",")]
        mgr.compress_files(source_list, dest, type)
        console.print(f"[green]Compressed to {dest}[/green]")
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")

@app.command()
def files_extract(source: str, dest: str):
    """Extract an archive to a destination."""
    client = get_client()
    mgr = FileManager(client)
    try:
        mgr.extract_files(source, dest)
        console.print(f"[green]Extracted {source} to {dest}[/green]")
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")

@app.command()
def files_chmod(path: str, perms: str):
    """Change permissions (e.g. 0755)."""
    client = get_client()
    mgr = FileManager(client)
    try:
        mgr.change_permissions(path, perms)
        console.print(f"[green]Changed permissions of {path} to {perms}[/green]")
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")

if __name__ == "__main__":
    app()




