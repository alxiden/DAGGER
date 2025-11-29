import socket
import threading
import datetime
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox


class NetworkTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=8, pady=6)

        # DNS resolution
        dns_label = ttk.Label(frm, text="Domain / Host:")
        dns_label.grid(row=0, column=0, sticky=tk.W)
        self.domain_entry = ttk.Entry(frm, width=50)
        self.domain_entry.grid(row=0, column=1, sticky=tk.W)
        btn_resolve = ttk.Button(frm, text="Resolve DNS", command=self._resolve)
        btn_resolve.grid(row=0, column=2, padx=6)

        # TCP connect
        ip_label = ttk.Label(frm, text="IP:")
        ip_label.grid(row=1, column=0, sticky=tk.W)
        self.ip_entry = ttk.Entry(frm, width=30)
        self.ip_entry.grid(row=1, column=1, sticky=tk.W)
        port_label = ttk.Label(frm, text="Port:")
        port_label.grid(row=1, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(frm, width=8)
        self.port_entry.grid(row=1, column=3, sticky=tk.W)
        btn_connect = ttk.Button(frm, text="TCP Connect", command=self._tcp_connect)
        btn_connect.grid(row=1, column=4, padx=6)

        # HTTP GET
        url_label = ttk.Label(frm, text="HTTP URL:")
        url_label.grid(row=2, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(frm, width=60)
        self.url_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        btn_http = ttk.Button(frm, text="HTTP GET", command=self._http_get)
        btn_http.grid(row=2, column=4)

        # Log output
        self.out = tk.Text(self, height=18, wrap=tk.NONE)
        self.out.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _append(self, line: str):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.out.insert(tk.END, f"{ts} {line}\n")
        self.out.see(tk.END)

    def _resolve(self):
        host = self.domain_entry.get().strip()
        if not host:
            messagebox.showinfo("Input required", "Please enter a domain/host to resolve.")
            return

        def worker():
            try:
                ip = socket.gethostbyname(host)
                msg = f"DNS resolved {host} -> {ip}"
                self._append(msg)
                self.app._log(msg)
            except Exception as e:
                msg = f"DNS resolve error for {host}: {e}"
                self._append(msg)
                self.app._log(msg)

        threading.Thread(target=worker, daemon=True).start()

    def _tcp_connect(self):
        ip = self.ip_entry.get().strip()
        port_raw = self.port_entry.get().strip()
        if not ip or not port_raw:
            messagebox.showinfo("Input required", "Please enter IP and port.")
            return
        try:
            port = int(port_raw)
        except ValueError:
            messagebox.showerror("Invalid port", "Please enter a valid numeric port.")
            return

        if not self.app.allow_external and not ip.startswith("127.") and ip != "localhost":
            messagebox.showwarning("Blocked", "External network connections are blocked. Check the allow external option to enable.")
            return

        def worker():
            try:
                with socket.create_connection((ip, port), timeout=5) as s:
                    msg = f"TCP connect success to {ip}:{port}"
                    self._append(msg)
                    self.app._log(msg)
            except Exception as e:
                msg = f"TCP connect failed to {ip}:{port} - {e}"
                self._append(msg)
                self.app._log(msg)

        threading.Thread(target=worker, daemon=True).start()

    def _http_get(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showinfo("Input required", "Please enter a URL.")
            return

        # very conservative: block external unless allowed
        if not self.app.allow_external:
            parsed = urllib.request.urlparse(url)
            host = parsed.hostname
            if host and host not in ("localhost", "127.0.0.1"):
                messagebox.showwarning("Blocked", "External HTTP requests are blocked by default.")
                return

        def worker():
            try:
                with urllib.request.urlopen(url, timeout=8) as r:
                    info = r.read(512)
                    msg = f"HTTP GET {url} status={r.status} len={len(info)}"
                    self._append(msg)
                    self.app._log(msg)
            except Exception as e:
                msg = f"HTTP GET failed {url} - {e}"
                self._append(msg)
                self.app._log(msg)

        threading.Thread(target=worker, daemon=True).start()
