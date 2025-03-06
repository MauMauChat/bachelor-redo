#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import requests
import shutil

# Konstante für den Modellnamen (anpassen, wie gewünscht)
MODEL_NAME = "llama3.2:3b"

# Basisinstallationsverzeichnis relativ zum Skript (von "src" aus)
# Das Skript liegt in .../project/src/model_integration,
# Wir erstellen einen Ordner "ollama_installation" innerhalb dieses Verzeichnisses.
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ollama_installation")
# Optional: Modellverzeichnis innerhalb des BASE_DIR – falls du zusätzliche Dateien ablegen möchtest
MODEL_DIR = os.path.join(BASE_DIR, "models", MODEL_NAME)


def download_file(url, dest_path):
    """Lädt eine Datei von der URL herunter und speichert sie unter dest_path."""
    print(f"Lade Datei von {url} herunter …")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Datei gespeichert: {dest_path}")


def install_ollama():
    """
    Installiert Ollama plattformunabhängig:

    - Unter Linux wird 'curl -fsSL https://ollama.com/install.sh | sh' ausgeführt.
    - Unter Windows wird angenommen, dass die Installer-Datei unter
      /home/lucy/Downloads/OllamaSetup.exe vorliegt und im Silent-Modus gestartet werden kann.
    """
    current_platform = platform.system()

    if current_platform == "Linux":
        print("Starte Installation von Ollama unter Linux …")
        cmd = "curl -fsSL https://ollama.com/install.sh | sh"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("Ollama wurde unter Linux installiert.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler bei der Linux-Installation von Ollama: {e}")
            sys.exit(1)
    elif current_platform == "Windows":
        print("Starte Installation von Ollama unter Windows …")
        # Pfad zur Installer-Datei (anpassen, falls nötig)
        installer_path = r"C:\Users\lucy\Downloads\OllamaSetup.exe"
        # Falls du das Skript in einer Umgebung mit Unix-Pfadtrennung hast,
        # kann das auch "/home/lucy/Downloads/OllamaSetup.exe" sein – passe das an!
        if not os.path.exists(installer_path):
            print(f"Installer nicht gefunden unter {installer_path}")
            sys.exit(1)
        try:
            # Starte den Installer im Silent-Modus (/S als Beispiel; ggf. anpassen)
            subprocess.run([installer_path, "/S"], check=True)
            print("Ollama wurde unter Windows installiert.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler bei der Windows-Installation von Ollama: {e}")
            sys.exit(1)
    else:
        print("Betriebssystem nicht unterstützt.")
        sys.exit(1)


def install_model():
    """
    Führt den Befehl 'ollama run MODEL_NAME' aus, um das Modell zu laden.
    Es wird davon ausgegangen, dass nach der Ollama-Installation der Befehl 'ollama'
    im PATH verfügbar ist.
    """
    # Überprüfe, ob der Befehl 'ollama' erreichbar ist.
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Ollama scheint nicht im PATH zu sein. Bitte Installation prüfen.")
        sys.exit(1)
    except FileNotFoundError:
        print("Ollama-Befehl nicht gefunden. Bitte Installation prüfen.")
        sys.exit(1)

    # Baue den Befehl, um das Modell zu laden
    cmd = ["ollama", "run", MODEL_NAME]
    print(f"Führe Befehl aus: {' '.join(cmd)}")
    try:
        # Hier wird der Befehl ausgeführt – beachte, dass 'ollama run' je nach Modellgröße blockierend sein kann.
        subprocess.run(cmd, check=True)
        print(f"Modell '{MODEL_NAME}' wurde erfolgreich geladen/initialisiert.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Laden des Modells: {e}")
        sys.exit(1)


def main():
    # Erstelle BASE_DIR falls noch nicht vorhanden
    os.makedirs(BASE_DIR, exist_ok=True)
    print("Starte den Installationsprozess von Ollama und dem Modell …")
    install_ollama()
    install_model()
    print("Installation und Modell-Integration abgeschlossen.")


if __name__ == "__main__":
    main()
