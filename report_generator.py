from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd


def generate_plots(df: pd.DataFrame, output_folder: str) -> Dict[str, str]:
    os.makedirs(output_folder, exist_ok=True)
    saved_files: Dict[str, str] = {}

    rails = ["3.3V", "5V", "12V"]

    plt.figure(figsize=(10, 5))
    for rail in rails:
        plt.plot(df["time_s"], df[f"{rail}_voltage"], label=f"{rail} Voltage")
    plt.plot(df["time_s"], df["input_voltage"], label="Input Voltage", linestyle="--", color="black")
    plt.title("Voltages vs. Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.legend()
    plt.grid(True)
    voltage_plot_path = os.path.join(output_folder, "voltages.png")
    plt.tight_layout()
    plt.savefig(voltage_plot_path)
    plt.close()
    saved_files["voltages"] = voltage_plot_path

    plt.figure(figsize=(10, 5))
    for rail in rails:
        plt.plot(df["time_s"], df[f"{rail}_current"], label=f"{rail} Current")
    plt.title("Currents vs. Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Current (A)")
    plt.legend()
    plt.grid(True)
    current_plot_path = os.path.join(output_folder, "currents.png")
    plt.tight_layout()
    plt.savefig(current_plot_path)
    plt.close()
    saved_files["currents"] = current_plot_path

    plt.figure(figsize=(10, 4))
    plt.plot(df["time_s"], df["input_voltage"], label="Solar Input Voltage", color="tab:orange")
    plt.title("Solar Input Voltage vs. Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.legend()
    plt.grid(True)
    input_plot_path = os.path.join(output_folder, "input_voltage.png")
    plt.tight_layout()
    plt.savefig(input_plot_path)
    plt.close()
    saved_files["input_voltage"] = input_plot_path

    return saved_files


def generate_report(df: pd.DataFrame, faults: List[str], output_folder: str) -> str:
    os.makedirs(output_folder, exist_ok=True)
    summary_lines: List[str] = []
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_lines.append("# EPS Test Summary")
    summary_lines.append(f"- Report generated: {start_time}")
    summary_lines.append(f"- Duration: {df['time_s'].iloc[-1]} seconds")
    summary_lines.append(f"- Faults detected: {len(faults)}")
    for fault in faults:
        summary_lines.append(f"  - {fault}")
    summary_lines.append("\n## Per-rail statistics")

    for rail in ["3.3V", "5V", "12V"]:
        summary_lines.append(f"### {rail}\n")
        summary_lines.append(f"- Voltage min: {df[f'{rail}_voltage'].min():.3f} V\n")
        summary_lines.append(f"- Voltage max: {df[f'{rail}_voltage'].max():.3f} V\n")
        summary_lines.append(f"- Voltage mean: {df[f'{rail}_voltage'].mean():.3f} V\n")
        summary_lines.append(f"- Current min: {df[f'{rail}_current'].min():.3f} A\n")
        summary_lines.append(f"- Current max: {df[f'{rail}_current'].max():.3f} A\n")
        summary_lines.append(f"- Current mean: {df[f'{rail}_current'].mean():.3f} A\n")
        summary_lines.append("\n")

    summary_lines.append("## Pass / Fail Criteria\n")
    summary_lines.append("- Pass if no rail dropped below 95% of nominal during sunlight.\n")
    summary_lines.append("- Pass if no overcurrent event exceeded limit.\n")
    summary_lines.append("- Pass if no temperature exceeded 80°C for an extended period.\n")

    summary_path = os.path.join(output_folder, "summary_report.md")
    with open(summary_path, "w", encoding="utf-8") as report_file:
        report_file.writelines(line + "\n" for line in summary_lines)

    return summary_path
