#!/usr/bin/env python3
import subprocess
import csv

NUM_RUNS = 100
all_runs_logs = []

# Führe die "ollama_integration.py" 100-mal aus und sammle die Log-Ausgaben (stdout)
for i in range(NUM_RUNS):
    print(f"Run {i+1} startet...")
    result = subprocess.run(["python", "ollama_integration.py"], capture_output=True, text=True)
    # Wir nehmen an, dass die relevanten Log-Meldungen in stdout erscheinen.
    log_lines = result.stdout.splitlines()
    all_runs_logs.append(log_lines)
    print(f"Run {i+1} abgeschlossen, {len(log_lines)} Zeilen.")

# Bestimme die maximale Zeilenanzahl aller Runs
max_lines = max(len(run) for run in all_runs_logs)

# Fülle kürzere Runs mit leeren Zeilen auf, damit alle Listen gleich lang sind
for run in all_runs_logs:
    while len(run) < max_lines:
        run.append("")

# Schreibe die kombinierten Logs in eine CSV-Datei, wobei jede Spalte einen Run repräsentiert
output_csv = "combined_logs.csv"
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=";")
    # Schreibe die Kopfzeile (Run 1, Run 2, …, Run 100)
    header = [f"Run {i+1}" for i in range(NUM_RUNS)]
    writer.writerow(header)
    # Für jede Zeile, schreibe die entsprechende Zeile aus jedem Run nebeneinander
    for line_idx in range(max_lines):
        row = [all_runs_logs[run_idx][line_idx] for run_idx in range(NUM_RUNS)]
        writer.writerow(row)

print(f"Combined logs written to {output_csv}")
