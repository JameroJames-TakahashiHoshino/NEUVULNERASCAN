import requests
from tqdm import tqdm


class DirectoryScanner:
    def __init__(self, target):
        self.target = target.rstrip("/")
        self.found = []

    def scan(self):
        wordlist = ["admin", "login", "uploads", "config", "backup"]

        for directory in tqdm(wordlist, desc="Bruteforcing Dirs"):
            url = f"{self.target}/{directory}"
            try:
                r = requests.get(url, timeout=5)
            except requests.exceptions.RequestException:
                # Network error – skip this directory and continue scanning
                continue

            if r.status_code == 200:
                self.found.append(url)

        return self.found
