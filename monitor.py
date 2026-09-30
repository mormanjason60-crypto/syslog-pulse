import datetime
import os
import sys
import psutil


def get_system_metrics():
    """Fetches real-time hardware telemetry."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()

    metrics = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage_pct": cpu_usage,
        "ram_total_gb": round(memory_info.total / (1024**3), 2),
        "ram_used_gb": round(memory_info.used / (1024**3), 2),
        "ram_usage_pct": memory_info.percent,
    }
    return metrics


def generate_markdown_report(metrics):
    """Formats metrics into a clean GitHub-ready Markdown file."""
    report_content = f"""# System Performance Snapshot

**Generated at:** `{metrics['timestamp']}`

## System Health Overview

| Metric | Current Value | Status |
| :--- | :--- | :--- |
| **CPU Usage** | {metrics['cpu_usage_pct']}% | {'⚠️ High Load' if metrics['cpu_usage_pct'] > 80 else '✅ Normal'} |
| **RAM Usage** | {metrics['ram_used_gb']} GB / {metrics['ram_total_gb']} GB ({metrics['ram_usage_pct']}%) | {'⚠️ High Usage' if metrics['ram_usage_pct'] > 80 else '✅ Normal'} |

---
*Generated automatically via `syslog-pulse` CLI*
"""
    with open("README.md", "w") as f:
        f.write(report_content)

    print("✅ System snapshot written to README.md")


if __name__ == "__main__":
    print("Gathering system telemetry...")
    data = get_system_metrics()
    generate_markdown_report(data)

