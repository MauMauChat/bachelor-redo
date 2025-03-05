#!/usr/bin/env python3
import logging
import csv

class CSVWriter:
    def __init__(self, filename):
        self.filename = filename
        logging.info(f"CSVWriter initialisiert mit Dateiname: {filename}")

    def write_rows(self, rows):
        try:
            fieldnames = ["i", "s", "c"]
            with open(self.filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
                    logging.info("Schreibe Zeile in CSV: " + str(row))
            logging.info(f"CSV-Datei {self.filename} erfolgreich geschrieben.")
        except Exception as e:
            logging.error("Fehler beim Schreiben der CSV-Datei: " + str(e))
