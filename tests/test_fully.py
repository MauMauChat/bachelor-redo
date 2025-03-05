import unittest
import logging
import os
import csv
from unittest.mock import patch, MagicMock
import pandas as pd

# Konstanten, die du anpassen kannst:
TEST_BATCH_SIZE = 20
TEST_MAX_BATCHES = 40
NUM_ROWS = TEST_BATCH_SIZE * TEST_MAX_BATCHES  # Anzahl der Zeilen in der Test-CSV
TEST_CSV_COLUMN = "'FREITEXT'"
EXPECTED_OUTPUT_ROWS_PER_BATCH = 2  # Da unsere gemockte AI-Antwort 2 Zeilen zurückliefert
EXPECTED_TOTAL_OUTPUT_ROWS = TEST_MAX_BATCHES * EXPECTED_OUTPUT_ROWS_PER_BATCH

# Importiere die OllamaProcessor-Klasse aus deinem Modul.
from project.src.model_integration.ollama_integration import OllamaProcessor

# Logging-Konfiguration für den Test
logging.basicConfig(
    level=logging.INFO,
    format='[TEST] %(asctime)s [%(levelname)s] %(message)s',
)


class TestOllamaProcessor(unittest.TestCase):
    def setUp(self):
        """
        Vor jedem Test: Erstelle eine Test-CSV mit NUM_ROWS Zeilen.
        """
        self.test_input_csv = 'test_input.csv'
        self.test_output_csv = 'test_output.csv'

        # Erstelle Testdaten, z.B. "Test sentence 1", "Test sentence 2", ...
        data = [{TEST_CSV_COLUMN: f"Test sentence {i}"} for i in range(1, NUM_ROWS + 1)]
        df = pd.DataFrame(data)

        # Logge die zu erstellenden Daten
        logging.info(f"Erstelle Test-CSV mit den Daten: {data}")

        # Schreibe die Test-CSV
        df.to_csv(self.test_input_csv, index=False, sep=";")

    # Optional: Nach jedem Test die Testdateien entfernen
    # def tearDown(self):
    #     if os.path.exists(self.test_input_csv):
    #         os.remove(self.test_input_csv)
    #     if os.path.exists(self.test_output_csv):
    #         os.remove(self.test_output_csv)

    # WICHTIG: Der Patch-Pfad muss exakt dem Importpfad entsprechen, der in deinem Modul verwendet wird.
    @patch('project.src.model_integration.ollama_integration.chat')
    def test_ollama_processor_with_mock(self, mock_chat):
        """
        Teste die OllamaProcessor-Klasse, wobei der Aufruf an ollama.chat() gemockt wird.
        """
        logging.info("Starte Test: test_ollama_processor_with_mock")

        # Erstelle ein Mock-Objekt, das wie ein ChatResponse-Objekt wirkt
        mock_response = MagicMock()
        # Liefere eine gültige XML-Antwort, die 2 Zeilen enthält (mit neuen Tags: <i>, <s>, <c>)
        mock_response.message.content = (
            "<result>\n"
            "  <i>1</i>\n"
            "  <s>Mocked Satz 1</s>\n"
            "  <c>Positiv</c>\n"
            "  <i>2</i>\n"
            "  <s>Mocked Satz 2</s>\n"
            "  <c>Neutral</c>\n"
            "</result>"
        )
        mock_chat.return_value = mock_response
        logging.info(f"Gemockte AI-Antwort gesetzt: {mock_response.message.content}")

        # Erstelle den Processor mit den definierten Konstanten
        processor = OllamaProcessor(
            input_csv=self.test_input_csv,
            output_csv=self.test_output_csv,
            batch_size=TEST_BATCH_SIZE,
            max_batches=TEST_MAX_BATCHES
        )

        logging.info(f"Processor erstellt mit input_csv={processor.input_csv}, "
                     f"output_csv={processor.output_csv}, batch_size={processor.batch_size}, "
                     f"max_batches={processor.max_batches}")

        # Führe den Prozess aus – intern wird ollama.chat() gemockt
        processor.run()

        # Überprüfe, ob die Output-CSV existiert
        self.assertTrue(os.path.exists(self.test_output_csv),
                        "Output CSV sollte nach processor.run() existieren.")

        # Lese den Inhalt der CSV, um die erwarteten Daten zu validieren
        with open(self.test_output_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)

        logging.info(f"Zeilen in der Output-CSV: {rows}")

        # Es sollten EXPECTED_TOTAL_OUTPUT_ROWS Zeilen vorhanden sein
        self.assertEqual(len(rows), EXPECTED_TOTAL_OUTPUT_ROWS,
                         f"Es sollten genau {EXPECTED_TOTAL_OUTPUT_ROWS} Zeilen in der CSV vorhanden sein.")

        # Überprüfe den Inhalt der einzelnen Zeilen anhand der gemockten Antwort
        # Hier werden die Felder 'i', 's' und 'c' überprüft
        self.assertEqual(rows[0]['i'], '1')
        self.assertEqual(rows[0]['c'], 'Positiv')
        self.assertEqual(rows[1]['i'], '2')
        self.assertEqual(rows[1]['c'], 'Neutral')

        # Da max_batches Aufrufe erwartet werden und jeder Aufruf die gemockte Antwort zurückliefert,
        # sollte der Chat-Aufruf genau TEST_MAX_BATCHES mal erfolgen.
        self.assertEqual(mock_chat.call_count, TEST_MAX_BATCHES,
                         f"ollama.chat sollte genau {TEST_MAX_BATCHES} mal aufgerufen werden.")

        logging.info("Test erfolgreich abgeschlossen.")


if __name__ == '__main__':
    unittest.main()
