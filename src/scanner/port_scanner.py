import os
import nmap
from tqdm import tqdm

class PortScanner:
    def __init__(self, target):
        self.target = target
        self.open_ports = {}

    def scan(self, port_range="1-1024"):
        # Try default Nmap lookup first; if that fails, try common Windows paths
        try:
            nm = nmap.PortScanner()
        except nmap.PortScannerError:
            # If Nmap isn't on PATH (common on Windows), try explicit locations
            possible_paths = [
                r"D:\\Nmapping\\nmap.exe",  # your custom install path
                r"C:\\Program Files (x86)\\Nmap\\nmap.exe",
                r"C:\\Program Files\\Nmap\\nmap.exe",
            ]
            nm = None
            for p in possible_paths:
                if os.path.exists(p):
                    # python-nmap expects a list/tuple of candidates, not a single string
                    nm = nmap.PortScanner(nmap_search_path=[p])
                    break
            if nm is None:
                # Re-raise the original error if no usable Nmap binary was found
                raise
        print(f"[+] Starting port scan on {self.target}")

        nm.scan(self.target, port_range)

        # Process scan results
        if self.target in nm.all_hosts():
            for proto in nm[self.target].all_protocols():
                ports = nm[self.target][proto].keys()
                for port in tqdm(ports, desc="Scanning Ports"):
                    state = nm[self.target][proto][port]['state']
                    if state == "open":
                        self.open_ports[port] = state

        return self.open_ports
