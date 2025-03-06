#!/usr/bin/env python3
import logging
import os
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from ollama import chat, ChatResponse
from prompt_builder import PromptBuilder
from response_parser import ResponseParser
from xlsx_writer import ExcelWriter

class OllamaProcessor:
    def __init__(self, input_csv, output_csv, batch_size=2, max_batches=2):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "..", "templates", "2024-09-30_Auswertung-Kommentare.xlsx")

        self.input_csv = input_csv
        self.output_csv = output_csv
        self.batch_size = batch_size
        self.max_batches = max_batches
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        self.csv_writer = ExcelWriter(template_path, output_csv)
        logging.info(f"OllamaProcessor initialisiert mit Input: {input_csv}, Output: {output_csv}, Batchgröße: {batch_size}, Max Batches: {max_batches}")

    def read_input(self):
        try:
            df = pd.read_csv(self.input_csv, encoding="utf-8", sep=";", on_bad_lines="skip")
            df = df.dropna(subset=["'FREITEXT'"])
            # Es werden nur so viele Zeilen eingelesen, wie Batches * Batchgröße vorgesehen sind
            freitexte = df["'FREITEXT'"].head(self.batch_size * self.max_batches).tolist()
            logging.info(f"Eingelesene Zeilen: {len(freitexte)}")
            return freitexte
        except Exception as e:
            logging.error("Fehler beim Einlesen der Eingabedatei: " + str(e))
            return []

    def call_ollama(self, prompt, batch_index):
        logging.info(f"Aufruf von ollama für Batch {batch_index}")
        # Wiederhole den KI-Aufruf im Fehlerfall, ohne den gesamten Prozess zu stoppen
        while True:
            try:
                response: ChatResponse = chat(model="llama3.2:3b", messages=[{'role': 'user', 'content': prompt}])
                response_text = response.message.content
                logging.info(f"Ollama-Antwort für Batch {batch_index} empfangen: {response_text[:100]}...")
                return response_text
            except Exception as e:
                logging.error(f"Fehler beim Aufruf von ollama in Batch {batch_index}: {e}. Neuer Versuch...")
                time.sleep(2)

    def process_batches(self):
        freitexte = self.read_input()
        if not freitexte:
            return {}
        batches = [freitexte[i:i + self.batch_size] for i in range(0, len(freitexte), self.batch_size)]
        batches = batches[:self.max_batches]
        results = {}
        current_id = 1
        with ThreadPoolExecutor(max_workers=self.max_batches) as executor:
            futures = {}
            for idx, batch in enumerate(batches, start=1):
                prompt = self.prompt_builder.build_prompt(batch, current_id)
                futures[executor.submit(self.call_ollama, prompt, idx)] = (idx, current_id)
                logging.info(f"Batch {idx} gestartet mit Start-ID {current_id}")
                current_id += len(batch)
            for future in as_completed(futures):
                batch_idx, _ = futures[future]
                res = future.result()
                results[batch_idx] = res
        return results

    def run(self):
        results = self.process_batches()
        all_rows = []
        for batch_idx in sorted(results.keys()):
            response_text = results[batch_idx]
            if not response_text:
                continue
            xml_content = self.response_parser.extract_result_xml(response_text)
            if not xml_content:
                continue
            rows = self.response_parser.parse_xml(xml_content)
            all_rows.extend(rows)
        self.csv_writer.write_rows(all_rows)
