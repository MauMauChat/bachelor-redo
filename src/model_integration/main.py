#!/usr/bin/env python3
import logging
import argparse
import atexit
import os

from ollama_processor import OllamaProcessor
from ollama_server import ensure_ollama_is_running, kill_process_on_port

def main():
    # Ollama-Server starten/neu starten
    ensure_ollama_is_running()

    # Beim Programmende sicherheitshalber den Ollama-Server-Port wieder killen.
    atexit.register(kill_process_on_port, 11434)

    parser = argparse.ArgumentParser(description="Ollama KI Batch Processor")
    parser.add_argument("--batch_size", type=int, default=10, help="Anzahl der Zeilen pro Batch")
    parser.add_argument("--max_batches", type=int, default=2, help="Anzahl der Batches (simulierte Threads)")
    args = parser.parse_args()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(current_dir, "..", "data", "FB Freitextantworten.csv")
    output_xlsx = "output.xlsx"

    processor = OllamaProcessor(
        input_csv,
        output_xlsx,
        batch_size=args.batch_size,
        max_batches=args.max_batches
    )

    processor.run()

if __name__ == "__main__":
    main()
