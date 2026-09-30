import argparse
import datetime
import json
import os
import sys
import psutil


def get_system_metrics(interval=1):
    """Fetches real-time hardware telemetry over a specified interval."""
    cpu_usage = psutil.cpu_percent(interval=interval)
    memory_info = psutil.virtual_memory()

    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage_pct": cpu_usage,
        "ram_total_gb": round(memory_info.total / (1024**3), 2),
        "ram_used_gb": round(memory_info.used / (1024**3), 2),
        "ram_usage_pct": memory_info.percent,
    }


def analyze_log_file(log_path):
    """Scans a log file for critical error keywords."""
    if not os.path.exists(log_path):
        print(f"⚠️ Log file not found: {log_path}")
        return {"error": "File not found", "critical_count": 0}

    keywords = ["ERROR", "CRITICAL", "FAILED", "WARNING"]
    summary = {"ERROR": 0, "CRITICAL": 0, "FAILED": 0, "WARNING": 0}

    with open(log_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            for word in keywords:
                if word in line:
                    summary[word] += 1

    return summary


def export_markdown(metrics, log_summary=None):
    """Formats metrics and log analysis into a clean Markdown file."""
    log_section = ""
    if log_summary:
        log_section = f"""
## System Log Analysis

| Keyword | Occurrences |
| :--- | :--- |
| **CRITICAL** | {log_summary.get('CRITICAL', 0)} |
| **ERROR** | {log_summary.get('ERROR', 0)} |
| **FAILED** | {log_summary.get('FAILED', 0)} |
| **WARNING** | {log_summary.get('WARNING', 0)} |
"""

    report_content = f"""# System Performance Snapshot

**Generated at:** `{metrics['timestamp']}`

## System Health Overview

| Metric | Current Value | Status |
| :--- | :--- | :--- |
| **CPU Usage** | {metrics['cpu_usage_pct']}% | {'⚠️ High Load' if metrics['cpu_usage_pct'] > 80 else '✅ Normal'} |
| **RAM Usage** | {metrics['ram_used_gb']} GB / {metrics['ram_total_gb']} GB ({metrics['ram_usage_pct']}%) | {'⚠️ High Usage' if metrics['ram_usage_pct'] > 80 else '✅ Normal'} |
{log_section}
---
*Generated automatically via `syslog-pulse` CLI*
"""
    with open("README.md", "w") as f:
        f.write(report_content)

    print("✅ System snapshot written to README.md")


def export_json(metrics, log_summary=None):
    """Exports system telemetry as structured JSON data."""
    payload = {"metrics": metrics, "log_summary": log_summary}
    with open("metrics.json", "w") as f:
        json.dump(payload, f, indent=4)
    print("✅ System metrics exported to metrics.json")


def main():
    parser = argparse.ArgumentParser(
        description="syslog-pulse: Infrastructure Telemetry & Log Parsing CLI Tool"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Sampling interval in seconds for CPU usage (default: 1)",
    )
    parser.add_argument(
        "--format",
        choices=["md", "json"],
        default="md",
        help="Output file format: 'md' for Markdown report or 'json' for raw data (default: md)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to a system log file to analyze for errors",
    )

    args = parser.parse_args()

    print(f" Gathering system telemetry over {args.interval}s interval...")
    metrics = get_system_metrics(interval=args.interval)

    log_summary = None
    if args.log_file:
        print(f"🔍 Analyzing log file: {args.log_file}...")
        log_summary = analyze_log_file(args.log_file)

    if args.format == "json":
        export_json(metrics, log_summary)
    else:
        export_markdown(metrics, log_summary)


if __name__ == "__main__":
    main()

