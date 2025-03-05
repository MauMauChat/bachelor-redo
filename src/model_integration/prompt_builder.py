#!/usr/bin/env python3
import logging
from prompt import PROMPT_TEMPLATE

class PromptBuilder:
    def __init__(self):
        self.prompt_template = PROMPT_TEMPLATE
        logging.info("PromptBuilder initialisiert. Vorlage gesetzt.")

    def build_prompt(self, batch, start_id):
        satz_text = ""
        for i, satz in enumerate(batch, start=start_id):
            satz_text += f"\\n{i}: {satz}"
        prompt = self.prompt_template + satz_text
        logging.info(f"Prompt erstellt für Start-ID {start_id}: {prompt[:100]}...")
        return prompt
