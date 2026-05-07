import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from typing import Dict, List

def generate_plots(df: pd.DataFrame, output_folder: str) -> Dict[str, str]:
    os.makedirs(output_folder, exist_ok=True)
    saved_files: Dict[str, str] = {}
    plt.figure(figsize=(10, 5))
    for rail in ["3.3V", "5V", "12V"]: plt.plot(df["time_s"] / 60, df[f"{rail}_voltage"], label=f"{rail} Rail")
    plt.plot(df["time_s"] / 60, df["battery_voltage"], label="Battery Bus", linestyle="--", color="black")
    plt.title("System Voltages"); plt.xlabel("Time (minutes)"); plt.ylabel("Voltage (V)"); plt.legend(); plt.grid(True)
    plt.savefig(os.path.join(output_folder, "voltages.png")); plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"] / 60, df["battery_soc"] * 100, color="tab:green", linewidth=2)
    plt.title("Battery State of Charge"); plt.xlabel("Time (minutes)"); plt.ylabel("SoC (%)"); plt.ylim(0, 105); plt.grid(True)
    plt.savefig(os.path.join(output_folder, "battery_soc.png")); plt.close()
    saved_files["soc"] = os.path.join(output_folder, "battery_soc.png")

    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"] / 60, df["solar_power_w"], label="Solar Gen", color="orange")
    plt.plot(df["time_s"] / 60, df["solar_power_w"] - df["net_power_w"], label="Load Consumption", color="red")
    plt.fill_between(df["time_s"] / 60, 0, df["solar_power_w"], alpha=0.1, color="orange")
    plt.title("Power Balance"); plt.xlabel("Time (minutes)"); plt.ylabel("Power (W)"); plt.legend(); plt.grid(True)
    plt.savefig(os.path.join(output_folder, "power_balance.png")); plt.close()
    saved_files["power"] = os.path.join(output_folder, "power_balance.png")
    return saved_files

def generate_report(df: pd.DataFrame, faults: List[str], output_folder: str) -> str:
    summary_lines = [
        "# High-Fidelity CubeSat EPS Simulation Report",
        f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Orbit Duration**: {df['time_s'].iloc[-1]/60:.1f} minutes",
        f"- **Final SoC**: {df['battery_soc'].iloc[-1]*100:.1f}%",
        f"- **Fault Events**: {len(faults)}"
    ]
    for fault in faults: summary_lines.append(f"  - {fault}")
    summary_path = os.path.join(output_folder, "summary_report.md")
    with open(summary_path, "w", encoding="utf-8") as f: f.writelines(line + "\n" for line in summary_lines)
    return summary_path
