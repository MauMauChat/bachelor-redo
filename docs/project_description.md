project/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   └── config.py           # Konfigurationsdateien (Pfaddefinitionen, Parameter)
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── file_manager.py     # Verwaltung der Dateipfade und -formate (Excel, Word, MD, TXT)
│   │   ├── excel_handler.py    # Verarbeitung von Excel-Dateien
│   │   ├── word_handler.py     # Verarbeitung von Word-Dokumenten
│   │   └── text_handler.py     # Verarbeitung von Markdown- und TXT-Dateien
│   ├── model_integration/
│   │   ├── __init__.py
│   │   └── ollama_integration.py  # Integration der Ollama CLI & Modelle (GPT‑40 äquivalent, Olama)
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── stats_integration.py   # Schnittstelle zu R für statistische Auswertungen
│   ├── template/
│   │   ├── __init__.py
│   │   ├── template_manager.py  # Verwaltung und Einbindung von Output-Templates (Markdown, XML)
│   │   └── xml_template.xml     # XML-Vorlage für Freitext-Kategorisierung
├── tests/
│   ├── test_file_manager.py
│   ├── test_excel_handler.py
│   ├── test_word_handler.py
│   ├── test_text_handler.py
│   ├── test_ollama_integration.py
│   └── test_stats_integration.py
├── docs/
│   ├── project_description.md   # Ausführliche Projektdokumentation (IMRaD-Format)
│   └── user_manual.md           # Bedienungsanleitung und Entwicklerdokumentation
├── templates/                   # Vorlagen für die finale Ausgabe (Markdown, XML, etc.)
│   ├── output_template.md
│   └── xml_template.xml
├── requirements.txt             # Auflistung aller Python-Abhängigkeiten
├── setup.py                     # Installation und Setup-Skript
└── README.md                    # Projektübersicht und -anleitung
