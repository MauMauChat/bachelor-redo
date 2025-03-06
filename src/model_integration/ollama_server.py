#!/usr/bin/env python3
import logging
import subprocess
import platform
import psutil

def kill_process_on_port(port: int = 11434):
    """
    Sucht plattformübergreifend nach Prozessen, die auf 'port' lauschen,
    und beendet diese (SIGKILL bzw. analog unter Windows).
    """
    for conn in psutil.net_connections():
        # Prüfen, ob der lokale Port übereinstimmt und ein Prozess zugeordnet ist
        if conn.laddr and conn.laddr.port == port and conn.pid:
            try:
                proc = psutil.Process(conn.pid)
                logging.info(f"Beende Prozess {conn.pid}, der auf Port {port} lauscht ...")
                proc.kill()
            except Exception as e:
                logging.error(f"Fehler beim Beenden des Prozesses {conn.pid} auf Port {port}: {e}")

def ensure_ollama_is_running():
    """
    Beendet vorhandene Prozesse auf Port 11434 (falls vorhanden)
    und startet dann 'ollama serve' neu im Hintergrund.
    """
    logging.info("Prüfe, ob ein Ollama-Server bereits aktiv ist ...")
    kill_process_on_port(11434)

    logging.info("Starte 'ollama serve' im Hintergrund ...")
    # Unter Windows ggf. ein neues Konsolenfenster starten
    creationflags = 0
    if platform.system() == "Windows":
        creationflags = subprocess.CREATE_NEW_CONSOLE
    subprocess.Popen(["ollama", "serve"], creationflags=creationflags)
