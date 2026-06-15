import argparse
from src.scanner.engine import NeuVulneraScanEngine
from src.scanner.report import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="NEU Vulnerability Scanner")
    parser.add_argument("--target", required=True, help="Target URL or IP")
    parser.add_argument("--json", action="store_true", help="Save JSON report")
    parser.add_argument("--txt", action="store_true", help="Save TXT report")

    args = parser.parse_args()

    engine = NeuVulneraScanEngine(args.target)
    results = engine.run_all()

    print("\nScan Completed!\n")

    report = ReportGenerator(args.target, results)

    if args.json:
        json_file = report.save_json()
        print(f"[+] JSON report saved: {json_file}")

    if args.txt:
        txt_file = report.save_txt()
        print(f"[+] TXT report saved: {txt_file}")

if __name__ == "__main__":
    main()
