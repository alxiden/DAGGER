import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

IS_WINDOWS = os.name == 'nt'


class MutexTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._lockfile = None
        self._mutex_handle = None
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=8, pady=6)

        name_label = ttk.Label(frm, text="Mutex name / lock name:")
        name_label.grid(row=0, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frm, width=50)
        self.name_entry.grid(row=0, column=1, sticky=tk.W)

        btn_create = ttk.Button(frm, text="Create Mutex", command=self._create_mutex)
        btn_create.grid(row=0, column=2, padx=6)
        btn_release = ttk.Button(frm, text="Release Mutex", command=self._release_mutex)
        btn_release.grid(row=0, column=3, padx=6)

        self.out = tk.Text(self, height=16, wrap=tk.NONE)
        self.out.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _append(self, line: str):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.out.insert(tk.END, f"{ts} {line}\n")
        self.out.see(tk.END)

    def _create_mutex(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showinfo("Input required", "Please enter a mutex/lock name.")
            return

        try:
            if IS_WINDOWS:
                import ctypes
                from ctypes import wintypes

                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                CreateMutex = kernel32.CreateMutexW
                CreateMutex.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
                CreateMutex.restype = wintypes.HANDLE
                handle = CreateMutex(None, False, name)
                if not handle:
                    raise OSError("CreateMutex failed")
                self._mutex_handle = handle
                msg = f"Created Windows mutex '{name}'"
            else:
                lockpath = os.path.join('/tmp', f"dagger_mutex_{name}.lock")
                fd = os.open(lockpath, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                self._lockfile = lockpath
                msg = f"Created lockfile '{lockpath}'"

            self._append(msg)
            self.app._log(msg)
        except FileExistsError:
            msg = f"Mutex/lock '{name}' already exists"
            self._append(msg)
            self.app._log(msg)
        except Exception as e:
            msg = f"Mutex create error: {e}"
            self._append(msg)
            self.app._log(msg)

    def _release_mutex(self):
        try:
            if IS_WINDOWS and self._mutex_handle:
                import ctypes
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                kernel32.CloseHandle(self._mutex_handle)
                self._mutex_handle = None
                msg = "Released Windows mutex"
            elif self._lockfile:
                os.remove(self._lockfile)
                msg = f"Removed lockfile {self._lockfile}"
                self._lockfile = None
            else:
                msg = "No mutex/lock to release"

            self._append(msg)
            self.app._log(msg)
        except Exception as e:
            msg = f"Mutex release error: {e}"
            self._append(msg)
            self.app._log(msg)
