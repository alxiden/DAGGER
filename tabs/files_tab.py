import os
import hashlib
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class FilesTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=8, pady=6)

        folder_label = ttk.Label(frm, text="Folder:")
        folder_label.grid(row=0, column=0, sticky=tk.W)
        self.folder_entry = ttk.Entry(frm, width=60)
        self.folder_entry.grid(row=0, column=1, sticky=tk.W)
        btn_browse = ttk.Button(frm, text="Browse", command=self._browse)
        btn_browse.grid(row=0, column=2, padx=6)

        name_label = ttk.Label(frm, text="Filename:")
        name_label.grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frm, width=60)
        self.name_entry.grid(row=1, column=1, sticky=tk.W)

        content_label = ttk.Label(frm, text="Content (optional):")
        content_label.grid(row=2, column=0, sticky=tk.NW)
        self.content_text = tk.Text(frm, height=6, width=60)
        self.content_text.grid(row=2, column=1, sticky=tk.W)

        btn_create = ttk.Button(frm, text="Create file", command=self._create_file)
        btn_create.grid(row=3, column=1, sticky=tk.W, pady=6)

        # output
        self.out = tk.Text(self, height=14, wrap=tk.NONE)
        self.out.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _browse(self):
        d = filedialog.askdirectory()
        if d:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, d)

    def _append(self, line: str):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.out.insert(tk.END, f"{ts} {line}\n")
        self.out.see(tk.END)

    def _create_file(self):
        folder = self.folder_entry.get().strip() or os.path.join(os.path.expanduser("~"), "temp_ioc")
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showinfo("Input required", "Please enter a filename.")
            return
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, name)
        content = self.content_text.get("1.0", tk.END)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            sha256 = self._sha256(path)
            msg = f"Created file {path} sha256={sha256}"
            self._append(msg)
            self.app._log(msg)
        except Exception as e:
            msg = f"File create error: {e}"
            self._append(msg)
            self.app._log(msg)

    @staticmethod
    def _sha256(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
