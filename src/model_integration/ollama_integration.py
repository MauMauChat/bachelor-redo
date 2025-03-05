#!/usr/bin/env python3
import os
import re
import csv
import pandas as pd
import logging
import time
import argparse
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
from ollama import chat, ChatResponse

# Konfiguriere Logging, sowohl in der Konsole als auch in einer Log-Datei
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="process.log",
    filemode="w"
)
# Zusätzlich in die Konsole loggen:
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)





def ensure_ollama_is_running():
    """
    Prüft, ob Ollama auf Port 11434 lauscht, und startet ihn ggf.
    Wartet dann bis zu 10 Sekunden, bis Ollama bereit ist.
    """


    logging.info("Kein Ollama-Server gefunden. Starte 'ollama serve' ...")
    # ollama serve im Hintergrund starten
    subprocess.Popen(["ollama", "serve"])





class PromptBuilder:
    def __init__(self):
        self.prompt_template = """**Prompt:**

**Analyze the following sentences and classify them into one of the given categories.**  
**One sentence, one category.**
**Output a well-formed XML snippet that contains a `<result>` tag. Inside `<result>`, for each sentence output exactly the following tags in order:**  
<result>
`<i>...</i>`  
`<s>...</s>`  
`<c>...</c>`  
</result>

**Available categories:**  
- Bezug auf LV  
- Nicht verständlich  
- Nicht eindeutig zuordenbar  
- Negativ  
- Positiv  
- Neutral, kein Kommentar, äquivalente Symbole, bedeutungslos  
- Anregungen, Wünsche  

**ALWAYS WRITE IT ONLY LIKE THIS. NOTHING MORE; NOTHING LESS:**  
<result>
  <i>1</i>
  <s>Die Vorlesung war sehr spannend und gut strukturiert.</s>
  <c>Positiv</c>
  <i>2</i>
  <s>???</s>
  <c>Nicht verständlich</c>
  <i>3</i>
  <s>Mehr praktische Beispiele wären hilfreich.</s>
  <c>Anregungen, Wünsche</c>
</result>


**Sentences:**
"""
        logging.info("PromptBuilder initialisiert. Vorlage gesetzt.")

    def build_prompt(self, batch, start_id):
        satz_text = ""
        for i, satz in enumerate(batch, start=start_id):
            satz_text += f"\n{i}: {satz}"
        prompt = self.prompt_template + satz_text
        logging.info(f"Prompt erstellt für Start-ID {start_id}: {prompt[:100]}...")
        return prompt


class ResponseParser:
    def __init__(self):
        logging.info("ResponseParser initialisiert.")

    def extract_result_xml(self, response_text):
        """
        Extrahiert den Inhalt zwischen <result> und </result> aus dem Response-Text.
        """
        match = re.search(r"<result>(.*?)</result>", response_text, flags=re.DOTALL)
        if match:
            result_xml = match.group(1).strip()
            logging.info(f"Extrahierter XML-Block: {result_xml[:100]}...")
            return result_xml
        else:
            logging.error("Kein <result> Tag gefunden.")
            return None

    def parse_xml(self, xml_content):
        """
        Parst den XML-Inhalt und extrahiert für jede Analyse die Tags <i>, <s> und <c>.
        """
        wrapped = f"<results>{xml_content}</results>"
        try:
            root = etree.fromstring(wrapped.encode("utf-8"))
            logging.info("XML erfolgreich geparst.")
        except Exception as e:
            logging.error("Fehler beim Parsen des XML: " + str(e))
            return []
        children = list(root)
        if len(children) % 3 != 0:
            logging.error(f"Ungültige Anzahl an XML-Elementen: {len(children)} (nicht durch 3 teilbar).")
            return []
        rows = []
        for i in range(0, len(children), 3):
            i_val = children[i].text.strip() if children[i].text else ""
            s_val = children[i+1].text.strip() if children[i+1].text else ""
            c_val = children[i+2].text.strip() if children[i+2].text else ""
            row = {"i": i_val, "s": s_val, "c": c_val}
            logging.info("Parsiere Zeile: " + str(row))
            rows.append(row)
        return rows


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


class OllamaProcessor:
    def __init__(self, input_csv, output_csv, batch_size=2, max_batches=2):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.batch_size = batch_size
        self.max_batches = max_batches
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        self.csv_writer = CSVWriter(output_csv)
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
        batches = [freitexte[i:i+self.batch_size] for i in range(0, len(freitexte), self.batch_size)]
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


def main():
    # Vor dem Start sichergehen, dass ollama serve läuft
    ensure_ollama_is_running()

    parser = argparse.ArgumentParser(description="Ollama KI Batch Processor")
    parser.add_argument("--batch_size", type=int, default=1, help="Anzahl der Zeilen pro Batch")
    parser.add_argument("--max_batches", type=int, default=15, help="Anzahl der Batches (simulierte Threads)")
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
