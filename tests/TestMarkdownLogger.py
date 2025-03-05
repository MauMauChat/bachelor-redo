import time
import unittest
import tempfile
from src/logging.MarkdownLogger import MarkdownLogger

class TestMarkdownLogger(unittest.TestCase):
    def test_log_auto_logs_actual_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = MarkdownLogger(log_dir=tmpdir)

            # Beispiel-Methode, die den Logger verwendet
            def sample_method(a, b):
                result = a * b
                logger.log_auto(log_level="DEBUG", args={"a": a, "b": b}, return_value=result)
                return result

            res = sample_method(5, 7)
            self.assertEqual(res, 35)

            # Warte kurz, um asynchrones Logging abzuschließen
            time.sleep(1.2)

            with open(logger.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Prüfe Header
            self.assertRegex(content, r"\| Schritt \| Log-Level \| Modul \| Filename \| Methodename \|")
            # Es sollten Header, Trennzeile und mindestens ein Logeintrag vorhanden sein
            lines = content.strip().splitlines()
            self.assertGreaterEqual(len(lines), 2)
            log_entry = lines[2]
            # Überprüfe, ob sample_method, "a: 5", "b: 7" und "35" im Logeintrag vorhanden sind
            self.assertIn("sample_method", log_entry)
            self.assertIn("a: 5", log_entry)
            self.assertIn("b: 7", log_entry)
            self.assertIn("35", log_entry)
            # Prüfe, ob das Log-Level "DEBUG" enthalten ist
            self.assertIn("DEBUG", log_entry)

if __name__ == '__main__':
    unittest.main()
