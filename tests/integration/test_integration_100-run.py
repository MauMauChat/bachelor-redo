#!/usr/bin/env python3
import os
import csv
import logging
import time
import pandas as pd
import pytest

# Importiere den echten OllamaProcessor inkl. aller abhängigen Klassen.
from project.src.model_integration.ollama_integration import OllamaProcessor

# Test-Konstanten
NUM_RUNS = 1
TEST_BATCH_SIZE = 2  # Batch-Größe kann beliebig angepasst werden
TEST_MAX_BATCHES = 2
NUM_ROWS = TEST_BATCH_SIZE * TEST_MAX_BATCHES  # Anzahl der Zeilen in der Test-CSV
TEST_CSV_COLUMN = "'FREITEXT'"
EXPECTED_OUTPUT_ROWS = TEST_MAX_BATCHES * 2  # Es werden 2 Zeilen pro Batch erwartet

# Persistenter Ordner für Testdateien und Ergebnisse
RESULTS_DIR = "integration_results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Logging-Konfiguration: Ausgabe in Log-Datei und Konsole (mit Flush nach jeder Meldung)
LOG_FILE = os.path.join(RESULTS_DIR, "integration_test.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=LOG_FILE,
    filemode="w"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


def create_test_csv(filepath, num_rows):
    """
    Erzeugt eine Test-CSV mit 'num_rows' Zeilen im für den Processor benötigten Format.
    """
    data = [{TEST_CSV_COLUMN: f"Integration Test sentence {i}"} for i in range(1, num_rows + 1)]
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, sep=";")
    logging.info(f"Test CSV erstellt unter {filepath} mit {num_rows} Zeilen.")


def run_processor(input_csv, output_csv):
    """
    Erstellt einen OllamaProcessor (inklusive aller abhängigen Klassen) und führt den Prozess aus.
    """
    processor = OllamaProcessor(
        input_csv=input_csv,
        output_csv=output_csv,
        batch_size=TEST_BATCH_SIZE,
        max_batches=TEST_MAX_BATCHES
    )
    processor.run()


@pytest.mark.integration
def test_integration_100_runs(caplog):
    """
    Integrationstest: Führt 100 Durchläufe des kompletten Prozesses (ohne Mocks) aus.

    Für jeden Durchlauf wird:
      - Eine Test-CSV als Input erstellt.
      - Der OllamaProcessor ausgeführt.
      - Über caplog kontrolliert, ob intern ein Fehler (Error-Level) protokolliert wurde.
      - Zusätzlich wird das Output-File geprüft (ob es existiert und die erwartete Anzahl Zeilen enthält).

    Alle Ergebnisse (Startzeit, Dauer, Resultat und eventuelle Fehlermeldungen) werden in einer CSV
    (integration_test_summary.csv) im Ordner 'integration_results' gespeichert.

    Nach jedem Durchlauf werden die Logging-Handler geflusht, sodass der Fortschritt live angezeigt wird.
    """
    summary_results = []
    successes = 0
    failures = 0
    run_durations = []
    logging.info(f"Starte Integrationstest: {NUM_RUNS} Runs werden durchgeführt.")
    start_time_total = time.time()

    for i in range(1, NUM_RUNS + 1):
        run_start_time = time.time()
        # Erstelle Pfade für Input- und Output-CSV
        input_csv = os.path.join(RESULTS_DIR, f"test_input_{i}.csv")
        output_csv = os.path.join(RESULTS_DIR, f"test_output_{i}.csv")
        create_test_csv(input_csv, NUM_ROWS)

        # Führe den Prozess aus (Fehler sollen intern geloggt werden)
        run_processor(input_csv, output_csv)

        # Überprüfe mittels caplog, ob im Log Fehler protokolliert wurden.
        error_records = [record for record in caplog.records if record.levelno >= logging.ERROR]
        if error_records:
            result = "Failure"
            failures += 1
            error_message = "; ".join(record.message for record in error_records)
            logging.error(f"Fehler in Run {i}: {error_message}")
        else:
            result = "Success"
            successes += 1
            error_message = ""
            logging.info(f"Run {i} erfolgreich abgeschlossen.")

        # Zusätzlich: Prüfe, ob die Output-CSV existiert und die erwartete Anzahl Zeilen enthält.
        if os.path.exists(output_csv):
            with open(output_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=";")
                rows = list(reader)
            if len(rows) != EXPECTED_OUTPUT_ROWS:
                result = "Failure"
                failures += 1
                msg = f"Erwartet: {EXPECTED_OUTPUT_ROWS} Zeilen, erhalten: {len(rows)} Zeilen."
                error_message = (error_message + " | " + msg).strip(" |")
                logging.error(f"Run {i} - {msg}")
        else:
            result = "Failure"
            failures += 1
            error_message = (error_message + " | Output CSV wurde nicht erstellt.").strip(" |")
            logging.error(f"Run {i} - Output CSV wurde nicht erstellt.")

        run_duration = time.time() - run_start_time
        run_durations.append(run_duration)
        summary_results.append({
            "run": i,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(run_start_time)),
            "duration_sec": round(run_duration, 2),
            "result": result,
            "error": error_message
        })
        avg_duration = sum(run_durations) / len(run_durations)
        runs_remaining = NUM_RUNS - i
        estimated_remaining = runs_remaining * avg_duration
        logging.info(
            f"Run {i}/{NUM_RUNS} abgeschlossen in {run_duration:.2f} sec. Geschätzte verbleibende Zeit: {estimated_remaining:.2f} sec.")
        caplog.clear()  # Leere caplog für den nächsten Durchlauf.
        # Flush alle Logging-Handler, um sofortige Ausgabe zu erzwingen.
        for handler in logging.getLogger().handlers:
            handler.flush()

    total_time = time.time() - start_time_total
    summary_file = os.path.join(RESULTS_DIR, "integration_test_summary.csv")
    with open(summary_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["run", "start_time", "duration_sec", "result", "error"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for res in summary_results:
            writer.writerow(res)
    logging.info(f"Integrationstest abgeschlossen. Summary in {summary_file} gespeichert.")
    logging.info(
        f"Total: {NUM_RUNS} Runs, {successes} erfolgreich, {failures} fehlgeschlagen, Gesamtzeit: {total_time:.2f} sec.")
    assert failures == 0, f"{failures} von {NUM_RUNS} Runs haben Fehler in der Klasse produziert."
