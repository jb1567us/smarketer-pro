import os
import subprocess
import json

class ScrapeBoxRunner:
    """
    Bridge to interact with ScrapeBox via CLI and Job files.
    """
    def __init__(self, scrapebox_path="C:\\ScrapeBox\\scrapebox.exe"):
        self.scrapebox_path = scrapebox_path
        self.jobs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "jobs", "scrapebox")
        os.makedirs(self.jobs_dir, exist_ok=True)

    def generate_automator_job(self, name, commands):
        """
        Generates a simplified Automator job file structure.
        NOTE: ScrapeBox .sba files are often complex, so we primarily 
        prepare the Keyword and Footprint files for the user or for a pre-made template.
        """
        job_path = os.path.join(self.jobs_dir, f"{name}.sba")
        # Placeholder for real SBA generation logic if schema is known.
        # For now, we document the JOB steps.
        with open(job_path, "w") as f:
            f.write(json.dumps(commands, indent=4))
        return job_path

    def prepare_data_files(self, name, keywords=None, footprints=None, proxies=None):
        """
        Prepares the .txt files that ScrapeBox consumes.
        """
        paths = {}
        if keywords:
            kw_path = os.path.join(self.jobs_dir, f"{name}_keywords.txt")
            with open(kw_path, "w") as f:
                f.write("\n".join(keywords))
            paths["keywords"] = kw_path

        if footprints:
            fp_path = os.path.join(self.jobs_dir, f"{name}_footprints.txt")
            with open(fp_path, "w") as f:
                f.write("\n".join(footprints))
            paths["footprints"] = fp_path

        if proxies:
            px_path = os.path.join(self.jobs_dir, f"{name}_proxies.txt")
            with open(px_path, "w") as f:
                f.write("\n".join(proxies))
            paths["proxies"] = px_path

        return paths

    def get_cli_command(self, job_file_path):
        """
        Returns the command string to run ScrapeBox with the given job.
        """
        return f'"{self.scrapebox_path}" -automator "{job_file_path}"'

    async def run_job(self, job_file_path):
        """
        Attempts to launch ScrapeBox.
        """
        if not os.path.exists(self.scrapebox_path):
            return {"status": "failed", "reason": "ScrapeBox executable not found at path."}
        
        try:
            cmd = self.get_cli_command(job_file_path)
            # Run detached or async?
            subprocess.Popen(cmd, shell=True)
            return {"status": "launched", "command": cmd}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
