import json
from datetime import datetime
import os
import re

class ReportGenerator:
    def __init__(self, target, results):
        self.target = target
        self.results = results

    def _safe_target_slug(self) -> str:
        """Return a filesystem-safe version of the target string.

        - Strip protocol (http/https)
        - Keep only hostname part before any path/query
        - Remove characters that are not alphanumerics, dot, or dash
        """
        raw = (self.target or "").strip()
        raw = raw.replace("https://", "").replace("http://", "")
        # Take only part before any path or query
        raw = raw.split("/", 1)[0]
        # Sanitize to safe characters
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", raw) or "target"
        return safe

    def save_json(self, directory="reports"):
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        target_slug = self._safe_target_slug()
        filename = f"{directory}/report_{target_slug}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)

        return filename

    def save_txt(self, directory="reports"):
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        target_slug = self._safe_target_slug()
        filename = f"{directory}/report_{target_slug}_{timestamp}.txt"

        with open(filename, "w") as f:
            f.write("NEU VULNERA SCAN REPORT\n")
            f.write("========================\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Generated: {timestamp}\n\n")

            for section, data in self.results.items():
                f.write(f"\n--- {section.upper()} ---\n")
                f.write(f"{json.dumps(data, indent=4)}\n")

        return filename
