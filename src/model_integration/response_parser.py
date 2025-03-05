#!/usr/bin/env python3
import logging
import re
from lxml import etree

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
