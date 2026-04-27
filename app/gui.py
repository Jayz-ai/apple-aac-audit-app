from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
import subprocess

from .workflow import RunConfig, RunResult, execute


class AuditApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Apple AAC 監査アプリ")
        self.root.geometry("920x720")

        self.input_path = tk.StringVar()
        self.report_path = tk.StringVar()
        self.target_sr = tk.IntVar(value=48000)
        self.auto_fix = tk.BooleanVar(value=True)
        self.state_text = tk.StringVar(value="状態: 待機中")
        self.current_step = tk.StringVar(value="現在の処理内容: -")
        self.progress_text = tk.StringVar(value="進行状況: 0%")
        self.last_log_time = time.time()
        self.worker: threading.Thread | None = None
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.last_result: RunResult | None = None

        self._build_ui()
        self._poll_events()
        self._watchdog()

    def _build_ui(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=8)

        tk.Button(top, text="WAVを選択", command=self.pick_input).grid(row=0, column=0, padx=4)
        tk.Entry(top, textvariable=self.input_path, width=90).grid(row=0, column=1, padx=4)

        tk.Button(top, text="保存先を選択", command=self.pick_reports).grid(row=1, column=0, padx=4)
        tk.Entry(top, textvariable=self.report_path, width=90).grid(row=1, column=1, padx=4)

        info = tk.LabelFrame(self.root, text="選択情報")
        info.pack(fill="x", padx=10, pady=8)
        self.file_name_label = tk.Label(info, text="参照確定ファイル名: -", anchor="w")
        self.file_name_label.pack(fill="x")
        self.folder_label = tk.Label(info, text="ファイルのフォルダパス: -", anchor="w")
        self.folder_label.pack(fill="x")
        self.report_folder_label = tk.Label(info, text="参照確定フォルダパス: -", anchor="w")
        self.report_folder_label.pack(fill="x")

        option = tk.LabelFrame(self.root, text="設定")
        option.pack(fill="x", padx=10, pady=8)
        tk.Label(option, text="target sample rate").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(option, text="48 kHz 推奨", variable=self.target_sr, value=48000).grid(row=0, column=1)
        tk.Radiobutton(option, text="44.1 kHz", variable=self.target_sr, value=44100).grid(row=0, column=2)
        tk.Checkbutton(option, text="自動補正ON/OFF", variable=self.auto_fix).grid(row=1, column=0, sticky="w")

        ctrl = tk.Frame(self.root)
        ctrl.pack(fill="x", padx=10, pady=8)
        tk.Button(ctrl, text="実行", command=self.start_run).pack(side="left", padx=4)
        self.open_report_btn = tk.Button(ctrl, text="レポートを開く", command=self.open_report, state="disabled")
        self.open_report_btn.pack(side="left", padx=4)
        self.open_folder_btn = tk.Button(ctrl, text="結果フォルダを開く", command=self.open_folder, state="disabled")
        self.open_folder_btn.pack(side="left", padx=4)

        st = tk.Frame(self.root)
        st.pack(fill="x", padx=10, pady=8)
        tk.Label(st, textvariable=self.state_text, anchor="w").pack(fill="x")
        tk.Label(st, textvariable=self.current_step, anchor="w").pack(fill="x")
        tk.Label(st, textvariable=self.progress_text, anchor="w").pack(fill="x")

        self.canvas = tk.Canvas(self.root, width=860, height=24, bg="white")
        self.canvas.pack(padx=10, pady=4)
        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, 24, fill="#4caf50")

        log_frame = tk.LabelFrame(self.root, text="ログ")
        log_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.log = tk.Text(log_frame, height=20)
        self.log.pack(fill="both", expand=True)

    def pick_input(self) -> None:
        p = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if not p:
            return
        self.input_path.set(p)
        pp = Path(p)
        self.file_name_label.config(text=f"参照確定ファイル名: {pp.name}")
        self.folder_label.config(text=f"ファイルのフォルダパス: {pp.parent}")

    def pick_reports(self) -> None:
        p = filedialog.askdirectory()
        if not p:
            return
        self.report_path.set(p)
        self.report_folder_label.config(text=f"参照確定フォルダパス: {p}")

    def start_run(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if not self.input_path.get() or not self.report_path.get():
            messagebox.showerror("エラー", "WAVと保存先を選択してください")
            return

        self.open_report_btn.config(state="disabled")
        self.open_folder_btn.config(state="disabled")
        self.state_text.set("状態: 処理中")
        self.current_step.set("現在の処理内容: 準備中")
        self._set_progress(0)
        self.log.delete("1.0", tk.END)
        self.last_log_time = time.time()

        cfg = RunConfig(
            input_wav=Path(self.input_path.get()),
            reports_root=Path(self.report_path.get()),
            target_sr=self.target_sr.get(),
            auto_remediate=self.auto_fix.get(),
        )

        def runner() -> None:
            try:
                result = execute(cfg, self._emit_log, self._emit_progress)
                self.events.put(("done", result))
            except Exception as exc:  # noqa: BLE001
                self.events.put(("error", str(exc)))

        self.worker = threading.Thread(target=runner, daemon=True)
        self.worker.start()

    def _emit_log(self, line: str) -> None:
        self.events.put(("log", line))

    def _emit_progress(self, pct: int, step: str) -> None:
        self.events.put(("progress", (pct, step)))

    def _poll_events(self) -> None:
        while True:
            try:
                kind, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self.last_log_time = time.time()
                self.log.insert(tk.END, str(payload).strip() + "\n")
                self.log.see(tk.END)
            elif kind == "progress":
                pct, step = payload  # type: ignore[misc]
                self.current_step.set(f"現在の処理内容: {step}")
                self._set_progress(int(pct))
            elif kind == "done":
                self.last_result = payload  # type: ignore[assignment]
                self.state_text.set("状態: 完了")
                self.open_report_btn.config(state="normal")
                self.open_folder_btn.config(state="normal")
            elif kind == "error":
                self.state_text.set("状態: エラー")
                self.log.insert(tk.END, f"エラー: {payload}\n")
        self.root.after(300, self._poll_events)

    def _watchdog(self) -> None:
        if self.state_text.get() == "状態: 処理中" and time.time() - self.last_log_time > 15:
            self.log.insert(tk.END, "処理継続中です。停止ではありません。\n")
            self.log.see(tk.END)
            self.last_log_time = time.time()
        self.root.after(1000, self._watchdog)

    def _set_progress(self, pct: int) -> None:
        pct = max(0, min(100, pct))
        self.progress_text.set(f"進行状況: {pct}%")
        width = int(860 * pct / 100)
        self.canvas.coords(self.progress_rect, 0, 0, width, 24)

    def open_report(self) -> None:
        if not self.last_result:
            return
        subprocess.run(["open", str(self.last_result.report_md)], check=False)

    def open_folder(self) -> None:
        if not self.last_result:
            return
        subprocess.run(["open", str(self.last_result.result_folder)], check=False)


def launch() -> None:
    root = tk.Tk()
    AuditApp(root)
    root.mainloop()
