#!/usr/bin/env python3
"""
Controlla ogni minuto lo stato di una run di GitHub Actions.
Premi 'c' e invio in qualsiasi momento per uscire.
"""

import json
import os
import threading
import time
import requests

# --- CONFIGURAZIONE ---
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "Serafinoxy/mia-app-kivy"
RUN_ID = "34283411855"
INTERVALLO_SECONDI = 60
HEADERS = {"Authorization": f"token {TOKEN}"}
# ----------------------

stop_flag = threading.Event()


def ascolta_uscita():
    """Gira in background: se l'utente scrive 'c' e preme invio, ferma lo script."""
    while not stop_flag.is_set():
        comando = input()
        if comando.strip().lower() == "c":
            stop_flag.set()
            break


def controlla_stato():
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{RUN_ID}"
    dati = requests.get(url, headers=HEADERS, timeout=15).json()
    return dati.get("status"), dati.get("conclusion"), dati.get("run_started_at")


def trova_job_id():
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{RUN_ID}/jobs"
    dati = requests.get(url, headers=HEADERS, timeout=15).json()
    jobs = dati.get("jobs", [])
    return jobs[0]["id"] if jobs else None


def ultime_righe_log(job_id, n=5):
    """Scarica il log corrente del job (anche a build in corso) e ritorna le ultime n righe utili.
    requests segue il redirect verso lo storage esterno togliendo l'header Authorization,
    evitando l'errore 403 di firma non valida."""
    url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job_id}/logs"
    risposta = requests.get(url, headers=HEADERS, timeout=15)
    testo = risposta.text

    righe = [r for r in testo.splitlines() if r.strip()]
    return righe[-n:] if righe else ["(nessuna riga di log ancora disponibile)"]


def main():
    print("Controllo la build ogni minuto. Scrivi 'c' e premi invio per uscire in qualsiasi momento.\n")

    thread_input = threading.Thread(target=ascolta_uscita, daemon=True)
    thread_input.start()

    inizio_controllo = time.time()

    while not stop_flag.is_set():
        try:
            status, conclusion, started_at = controlla_stato()
            if status != "completed":
                job_id = trova_job_id()
                righe = ultime_righe_log(job_id, n=5) if job_id else ["(job non trovato)"]
            else:
                righe = ["-"]
        except Exception as e:
            print(f"Errore nel controllare la build: {e}")
            status, conclusion, started_at, righe = None, None, None, [str(e)]

        minuti_passati = int((time.time() - inizio_controllo) / 60)
        orario = time.strftime("%H:%M:%S")

        print(f"\n[{orario}] (controllo #{minuti_passati + 1}) status={status}")
        print("Ultime righe del log:")
        for riga in righe:
            print(f"   {riga}")

        if status == "completed":
            print("\n--- BUILD TERMINATA ---")
            if conclusion == "success":
                print("✅ Successo! L'APK dovrebbe essere disponibile come artifact.")
            else:
                print(f"❌ Fallita (conclusion: {conclusion}). Controlla il log per i dettagli.")
            stop_flag.set()
            break

        stop_flag.wait(timeout=INTERVALLO_SECONDI)

    print("Script terminato.")


if __name__ == "__main__":
    main()
