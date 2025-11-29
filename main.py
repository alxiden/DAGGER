#!/usr/bin/env python3
"""DAGGER - IOC Simulator GUI

Safe, non-malicious toolkit to simulate Indicators of Compromise (IOCs)
for testing SIEM rules inside isolated VMs.

Features:
- Network tab: DNS resolve, TCP connect (to allowed targets), HTTP GET (optional external)
- Registry tab: read-only queries on Windows; simulated JSON store on non-Windows
- Files tab: create files with IOC-like names and content, compute SHA256
- Mutex tab: create/release a named mutex (Windows) or file-lock (cross-platform)
- Logs tab: view and save generated events for SIEM ingestion

Safety: by default external network operations are blocked; user must explicitly
allow external network usage. Run inside isolated lab VM.
"""
import os
import sys
import json
import socket
import threading
import hashlib
import datetime
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

IS_WINDOWS = sys.platform.startswith("win")

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "ioc_sim.log")

from tabs import NetworkTab, RegistryTab, FilesTab, MutexTab, LogsTab


def safe_append_log(line: str):
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{ts} {line}\n")


class IOCSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DAGGER - IOC Simulator")
        self.geometry("900x600")

        self.allow_external = tk.BooleanVar(value=False)

        self._build_ui()
        self._log("App started")

    def _build_ui(self):
        # Top frame with global options
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        ext_chk = ttk.Checkbutton(top, text="Allow external network (dangerous)", variable=self.allow_external)
        ext_chk.pack(side=tk.LEFT)

        btn_open_logs = ttk.Button(top, text="Open log file folder", command=self._open_log_folder)
        btn_open_logs.pack(side=tk.RIGHT)

        # Notebook for tabs
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        base_dir = os.path.dirname(__file__)
        sim_registry = os.path.join(base_dir, "sim_registry.json")

        self.network_tab = NetworkTab(nb, self)
        nb.add(self.network_tab, text="Network")

        self.registry_tab = RegistryTab(nb, self, store_path=sim_registry)
        nb.add(self.registry_tab, text="Registry")

        self.files_tab = FilesTab(nb, self)
        nb.add(self.files_tab, text="Files")

        self.mutex_tab = MutexTab(nb, self)
        nb.add(self.mutex_tab, text="Mutex")

        self.logs_tab = LogsTab(nb, self, log_path=LOG_PATH)
        nb.add(self.logs_tab, text="Logs")

    def _open_log_folder(self):
        path = os.path.abspath(LOG_DIR)
        if IS_WINDOWS:
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f"open {path}")
        else:
            os.system(f"xdg-open {path}")

    def _log(self, msg: str):
        safe_append_log(msg)
        try:
            self.logs_tab.append(msg)
        except Exception:
            pass

def main():
    app = IOCSimulatorApp()
    app.mainloop()


if __name__ == '__main__':
    main()
