import os
import json
import threading
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

IS_WINDOWS = os.name == 'nt'


class RegistryTab(ttk.Frame):
    def __init__(self, parent, app, store_path=None):
        super().__init__(parent)
        self.app = app
        # allow main to pass a store_path (cross-platform)
        self._store_path = store_path or os.path.join(os.path.dirname(__file__), "sim_registry.json")
        if not IS_WINDOWS:
            if not os.path.exists(self._store_path):
                with open(self._store_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=8, pady=6)

        key_label = ttk.Label(frm, text="Registry path / Key:")
        key_label.grid(row=0, column=0, sticky=tk.W)
        self.key_entry = ttk.Entry(frm, width=70)
        self.key_entry.grid(row=0, column=1, sticky=tk.W)
        btn_read = ttk.Button(frm, text="Query", command=self._query)
        btn_read.grid(row=0, column=2, padx=6)

        # value name
        name_label = ttk.Label(frm, text="Value name (optional):")
        name_label.grid(row=1, column=0, sticky=tk.W)
        self.value_entry = ttk.Entry(frm, width=40)
        self.value_entry.grid(row=1, column=1, sticky=tk.W)

        # output
        self.out = tk.Text(self, height=18, wrap=tk.NONE)
        self.out.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _append(self, line: str):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.out.insert(tk.END, f"{ts} {line}\n")
        self.out.see(tk.END)

    def _query(self):
        key = self.key_entry.get().strip()
        name = self.value_entry.get().strip() or None
        if not key:
            messagebox.showinfo("Input required", "Please enter a registry path or simulated key.")
            return

        def worker():
            try:
                if IS_WINDOWS:
                    import winreg

                    parts = key.split("\\\\", 1)
                    hive_name = parts[0]
                    sub = parts[1] if len(parts) > 1 else ""
                    hive = getattr(winreg, hive_name)
                    with winreg.OpenKey(hive, sub) as k:
                        if name:
                            val, _ = winreg.QueryValueEx(k, name)
                            msg = f"Registry {key} {name} = {val}"
                        else:
                            vals = []
                            try:
                                i = 0
                                while True:
                                    v = winreg.EnumValue(k, i)
                                    vals.append(f"{v[0]}={v[1]}")
                                    i += 1
                            except OSError:
                                pass
                            msg = f"Registry {key} values: {';'.join(vals)}"
                else:
                    with open(self._store_path, "r", encoding="utf-8") as f:
                        store = json.load(f)
                    entry = store.get(key, {})
                    if name:
                        v = entry.get(name, "<not present>")
                        msg = f"Simulated registry {key} {name} = {v}"
                    else:
                        msg = f"Simulated registry {key} = {json.dumps(entry)}"

                self._append(msg)
                self.app._log(msg)
            except Exception as e:
                msg = f"Registry query error: {e}"
                self._append(msg)
                self.app._log(msg)

        threading.Thread(target=worker, daemon=True).start()
