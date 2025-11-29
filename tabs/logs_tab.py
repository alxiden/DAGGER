import os
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class LogsTab(ttk.Frame):
    def __init__(self, parent, app, log_path=None):
        super().__init__(parent)
        self.app = app
        self._log_path = log_path
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=8, pady=6)

        btn_reload = ttk.Button(frm, text="Reload Log", command=self._reload)
        btn_reload.pack(side=tk.LEFT)
        btn_save = ttk.Button(frm, text="Save As...", command=self._save_as)
        btn_save.pack(side=tk.LEFT, padx=6)

        self.out = tk.Text(self, height=28, wrap=tk.NONE)
        self.out.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._reload()

    def append(self, msg: str):
        self.out.insert(tk.END, msg + "\n")
        self.out.see(tk.END)

    def _reload(self):
        self.out.delete("1.0", tk.END)
        if not self._log_path:
            self.out.insert(tk.END, "<no log path provided>\n")
            return
        try:
            with open(self._log_path, "r", encoding="utf-8") as f:
                self.out.insert(tk.END, f.read())
        except FileNotFoundError:
            self.out.insert(tk.END, "<no log found>\n")

    def _save_as(self):
        p = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log"), ("All files", "*")])
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.out.get("1.0", tk.END))
            messagebox.showinfo("Saved", f"Log saved to {p}")
