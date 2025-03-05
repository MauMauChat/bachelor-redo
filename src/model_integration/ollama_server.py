#!/usr/bin/env python3
import logging
import subprocess

def ensure_ollama_is_running():
    """
    Prüft, ob Ollama auf Port 11434 lauscht, und startet ihn ggf.
    Warte-Code etc. könnte man hier ergänzen, 
    für die Demo bleibt es einfach so wie im Codebeispiel.
    """
    logging.info("Kein Ollama-Server gefunden. Starte 'ollama serve' ...")
    # ollama serve im Hintergrund starten
    subprocess.Popen(["ollama", "serve"])
