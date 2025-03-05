import datetime
import inspect
import os
from concurrent.futures import ThreadPoolExecutor

class MarkdownLogger:
    """
    Erstellt pro Run eine Markdown-Logdatei im angegebenen Log-Verzeichnis.

    Der Dateiname enthält Datum und Uhrzeit (Format: log_YYYYMMDD_HHMMSS.md).
    Es wird eine Markdown-Tabelle mit den Spalten erstellt:
      - Schritt (0..n)
      - Log-Level
      - Modul
      - Filename
      - Methodename
      - Übergebene Argumente (Argumentname: tatsächlicher Wert)
      - Methoderückgabe (tatsächlicher Wert, oder "-" falls None)
      - Timestamp
    Zusätzlich werden die Log-Einträge asynchron in die Datei geschrieben.
    """

    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.file_path = os.path.join(self.log_dir, f"log_{timestamp}.md")
        self.step = 0
        self.executor = ThreadPoolExecutor(max_workers=1)

        header = ("| Schritt | Log-Level | Modul | Filename | Methodename | Übergebene Argumente | "
                  "Methoderückgabe | Timestamp |\n"
                  "|---------|-----------|-------|----------|-------------|----------------------|-----------------|-----------|\n")
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(header)

    def _write_log(self, line: str):
        \"\"\"Interne Methode: Schreibt synchron den Logeintrag in die Datei.\"\"\"
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(line)

    def log_auto(self, log_level: str = "INFO", args: dict = None, return_value=None):
        \"\"\"
        Fügt einen neuen Logeintrag als Zeile in die Markdown-Tabelle ein.
        Die Angaben zu Modul, Filename und Methodename werden automatisch ermittelt.
        Es werden die tatsächlichen übergebenen Werte und das tatsächliche Ergebnis geloggt.
        \"\"\"
        caller_frame = inspect.stack()[1]
        module_obj = inspect.getmodule(caller_frame.frame)
        module_name = module_obj.__name__ if module_obj else "-"
        filename = os.path.basename(caller_frame.filename)
        methodname = caller_frame.function
        entry_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.step += 1
        arg_str = ", ".join([f"{k}: {v}" for k, v in args.items()]) if args else "-"
        ret_str = str(return_value) if return_value is not None else "-"

        log_line = (f"| {self.step} | {log_level} | {module_name} | {filename} | {methodname} | "
                    f"{arg_str} | {ret_str} | {entry_timestamp} |\n")
        # Asynchrones Schreiben
        self.executor.submit(self._write_log, log_line)
