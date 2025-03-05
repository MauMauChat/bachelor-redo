import os
import datetime
import traceback
import threading
import inspect
from concurrent.futures import ThreadPoolExecutor

class GlobalError(Exception):
    """
    Globale Fehlerklasse für zentralisierte Fehlerbehandlung.

    Erfasst:
      - Fehlermeldung
      - Erwartetes Ergebnis
      - Log-Level (default: "ERROR")
      - Korrelations-ID (optional)
      - Zusätzliche Details (als Dictionary)
      - Zeitstempel, PID und Thread-ID
      - Modulname, Dateiname, Ordnername und Zeilennummer (automatisch ermittelt)
    """

    def __init__(self, message: str, expected_result: str = None, details: dict = None,
                 log_level: str = "ERROR", correlation_id: str = None):
        self.message = message
        self.expected_result = expected_result
        self.details = details or {}
        self.log_level = log_level
        self.correlation_id = correlation_id
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.pid = os.getpid()
        self.thread_id = threading.get_ident()

        # Hole relevante Stack-Information (letzte nicht-interne Aufrufstelle)
        tb = traceback.extract_stack(limit=3)[0]
        self.file = os.path.basename(tb.filename)  # Dateiname
        self.folder = os.path.basename(os.path.dirname(tb.filename))  # Name des unmittelbaren Ordners
        self.module = tb.name  # Funktionsname
        self.line = tb.lineno  # Zeilennummer

        super().__init__(message)

    def __str__(self):
        base = (f"[{self.timestamp}] [{self.log_level}] Fehler in '{self.folder}/{self.file}' "
                f"(Modul: {self.module}, Zeile: {self.line}) - Nachricht: {self.message} | "
                f"Erwartetes Ergebnis: {self.expected_result} | Details: {self.details} | "
                f"PID: {self.pid}, Thread: {self.thread_id}")
        if self.correlation_id:
            base += f" | Korrelations-ID: {self.correlation_id}"
        return base
