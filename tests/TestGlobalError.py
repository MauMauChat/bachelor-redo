import unittest
from src/error_handling.GlobalError import GlobalError

class TestGlobalError(unittest.TestCase):
    def test_global_error_str_contains_all_fields(self):
        def dummy_function():
            raise GlobalError(
                message="Testfehler aufgetreten.",
                expected_result="Erwarteter Wert",
                details={"key": "value"},
                correlation_id="CORR123"
            )

        try:
            dummy_function()
        except GlobalError as ge:
            error_str = str(ge)
            # Prüfe, ob wichtige Felder enthalten sind
            self.assertIn("Testfehler aufgetreten.", error_str)
            self.assertIn("Erwarteter Wert", error_str)
            self.assertIn("Details: {'key': 'value'}", error_str)
            self.assertIn("PID:", error_str)
            self.assertIn("Thread:", error_str)
            self.assertIn("Korrelations-ID: CORR123", error_str)
            # Prüfe, ob Timestamp im korrekten Format vorliegt
            self.assertRegex(error_str, r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")
            # Modul, Filename, Zeilennummer sollten vorhanden sein
            self.assertIn("Modul:", error_str)
            self.assertIn("Zeile:", error_str)

if __name__ == '__main__':
    unittest.main()
