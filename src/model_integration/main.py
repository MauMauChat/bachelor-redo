#!/usr/bin/env python3
import logging
import argparse
from ollama_processor import OllamaProcessor
from ollama_server import ensure_ollama_is_running

def main():
    # Vor dem Start sichergehen, dass ollama serve läuft
    ensure_ollama_is_running()

    parser = argparse.ArgumentParser(description="Ollama KI Batch Processor")
    parser.add_argument("--batch_size", type=int, default=5, help="Anzahl der Zeilen pro Batch")
    parser.add_argument("--max_batches", type=int, default=1, help="Anzahl der Batches (simulierte Threads)")
    args = parser.parse_args()

    input_csv = "/home/lucy/PycharmProjects/bachelorarbeit_redo/project/src/data/FB Freitextantworten.csv"
    output_csv = "output.csv"

    processor = OllamaProcessor(
        input_csv,
        output_csv,
        batch_size=args.batch_size,
        max_batches=args.max_batches
    )

    processor.run()

if __name__ == "__main__":
    main()
