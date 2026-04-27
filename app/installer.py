from __future__ import annotations

import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path


class InstallerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Apple AAC Audit App インストーラー")
        self.root.geometry("760x520")

        self.state = tk.StringVar(value="状態: 待機中")
        self.target_dir = Path(__file__).resolve().parent.parent

        tk.Label(root, text="Apple AAC Audit App セットアップ", font=("Helvetica", 16, "bold")).pack(pady=8)
        tk.Label(root, text=f"インストール対象: {self.target_dir}", anchor="w", justify="left").pack(fill="x", padx=10)
        tk.Label(
            root,
            text="このインストーラーは仮想環境(.venv)を作成し、requirements.txtをインストールします。",
            anchor="w",
            justify="left",
        ).pack(fill="x", padx=10, pady=(2, 10))

        btns = tk.Frame(root)
        btns.pack(fill="x", padx=10, pady=6)
        self.install_btn = tk.Button(btns, text="インストール開始", command=self.start_install)
        self.install_btn.pack(side="left")
        tk.Button(btns, text="閉じる", command=root.destroy).pack(side="left", padx=8)

        tk.Label(root, textvariable=self.state, anchor="w").pack(fill="x", padx=10)

        self.log = tk.Text(root, height=24)
        self.log.pack(fill="both", expand=True, padx=10, pady=8)

    def start_install(self) -> None:
        self.install_btn.config(state="disabled")
        self.state.set("状態: 処理中")
        threading.Thread(target=self._run_install, daemon=True).start()

    def _run_install(self) -> None:
        try:
            self._append(f"Python: {sys.executable}")
            self._run([sys.executable, "-m", "venv", ".venv"])
            vpy = self._resolve_venv_python()
            self._run([str(vpy), "-m", "pip", "install", "--upgrade", "pip"])
            self._run([str(vpy), "-m", "pip", "install", "-r", "requirements.txt"])
            self._append("セットアップ完了。次は launch_app.command をダブルクリックして起動してください。")
            self.root.after(0, lambda: self.state.set("状態: 完了"))
        except Exception as exc:  # noqa: BLE001
            self._append(f"エラー: {exc}")
            self.root.after(0, lambda: self.state.set("状態: エラー"))
        finally:
            self.root.after(0, lambda: self.install_btn.config(state="normal"))

    def _resolve_venv_python(self) -> Path:
        candidates = [
            self.target_dir / ".venv" / "bin" / "python3",
            self.target_dir / ".venv" / "bin" / "python",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError("仮想環境のPython実行ファイルが見つかりません。")

    def _run(self, args: list[str]) -> None:
        self._append("$ " + " ".join(args))
        result = subprocess.run(
            args,
            cwd=str(self.target_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout:
            self._append(result.stdout.strip())
        if result.stderr:
            self._append(result.stderr.strip())

    def _append(self, text: str) -> None:
        self.root.after(0, lambda: self._append_on_ui(text))

    def _append_on_ui(self, text: str) -> None:
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)


def launch_installer() -> None:
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_installer()
