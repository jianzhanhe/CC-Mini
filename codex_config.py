"""
CC-Mini  ——  Codex 一键切换
  • API 地址  （默认 http://api.h5.namawang.com/v1，可自定义）
  • API Key   （右侧「获取」按钮打开官网）
  • 模型名称  （可快速选择）
切换时：用 config.txt 模板覆写 config.toml（替换 base_url / model / review_model）
        API Key 写入 auth.json
"""

import json
import os
import re
import sys
import tkinter as tk
import webbrowser

CODEX_HOME  = os.path.join(os.path.expanduser("~"), ".codex")
AUTH_JSON   = os.path.join(CODEX_HOME, "auth.json")
CONFIG_TOML = os.path.join(CODEX_HOME, "config.toml")

# 兼容 PyInstaller 打包后的路径（--onefile 时资源在 sys._MEIPASS）
if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

SCRIPT_DIR  = _BASE
CONFIG_TPL  = os.path.join(_BASE, "config.txt")

DEFAULT_URL = "http://api.h5.namawang.com/v1"
KEY_SITE    = "http://api.h5.namawang.com"

QUICK_MODELS = [
    "gpt-5.5", "gpt-5.3-codex", "gpt-4o",
    "deepseek-v3", "deepseek-coder", "claude-sonnet-4-6",
]

C = {
    "bg":      "#13131f", "panel":    "#1a1a2e",
    "inp":     "#0f0f1a", "inp_bdr":  "#2a2a45",
    "accent":  "#6366f1", "accent_h": "#818cf8",
    "teal":    "#06b6d4", "teal_h":   "#22d3ee",
    "green":   "#10b981", "red":      "#ef4444",
    "fg":      "#e2e8f0", "fg_dim":   "#94a3b8",
    "fg_mute": "#475569", "border":   "#2a2a45",
    "chip":    "#1e293b", "chip_h":   "#2d3f55",
    "getbtn":  "#1e3a2e",
}


# ── 核心逻辑 ──────────────────────────────────────────────────────────────────

def _read_current():
    url, key, model = DEFAULT_URL, "", ""
    try:
        t = open(CONFIG_TOML, encoding="utf-8").read()
        m = re.search(r'^base_url\s*=\s*"([^"]*)"', t, re.MULTILINE)
        if m: url = m.group(1)
        m = re.search(r'^model\s*=\s*"([^"]*)"', t, re.MULTILINE)
        if m: model = m.group(1)
    except Exception: pass
    try:
        a = json.loads(open(AUTH_JSON, encoding="utf-8").read())
        k = a.get("OPENAI_API_KEY", "")
        if k and k != "PROXY_MANAGED": key = k
    except Exception: pass
    return url, key, model



def do_switch(api_url: str, api_key: str, model: str) -> str:
    try:
        tpl = open(CONFIG_TPL, encoding="utf-8").read()
        tpl = re.sub(r'^(base_url\s*=\s*)"[^"]*"',
                     lambda m: f'{m.group(1)}"{api_url.rstrip("/")}"',
                     tpl, flags=re.MULTILINE)
        def sub_m(m): return f'{m.group(1)}"{model}"'
        tpl = re.sub(r'^(model\s*=\s*)"[^"]*"',        sub_m, tpl, flags=re.MULTILINE)
        tpl = re.sub(r'^(review_model\s*=\s*)"[^"]*"', sub_m, tpl, flags=re.MULTILINE)
        os.makedirs(CODEX_HOME, exist_ok=True)
        with open(CONFIG_TOML, "w", encoding="utf-8") as f:
            f.write(tpl)
    except Exception as e:
        return f"config.toml 写入失败：{e}"
    try:
        try:    auth = json.loads(open(AUTH_JSON, encoding="utf-8").read())
        except: auth = {}
        auth["OPENAI_API_KEY"] = api_key
        with open(AUTH_JSON, "w", encoding="utf-8") as f:
            json.dump(auth, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except Exception as e:
        return f"auth.json 写入失败：{e}"
    return ""


# ── GUI ───────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CC-Mini")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.overrideredirect(True)
        self._dx = self._dy = 0
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = 500, 430
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _ds(self, e): self._dx, self._dy = e.x_root, e.y_root
    def _dm(self, e):
        self.geometry(f"+{self.winfo_x()+e.x_root-self._dx}"
                      f"+{self.winfo_y()+e.y_root-self._dy}")
        self._dx, self._dy = e.x_root, e.y_root

    # ── 构建 UI ───────────────────────────────────────────────────────────────
    def _build(self):
        # 标题栏
        hdr = tk.Frame(self, bg=C["panel"])
        hdr.pack(fill="x")
        hdr.bind("<ButtonPress-1>", self._ds)
        hdr.bind("<B1-Motion>",     self._dm)

        dot = tk.Canvas(hdr, width=12, height=12, bg=C["panel"], highlightthickness=0)
        dot.create_oval(1, 1, 11, 11, fill=C["teal"], outline="")
        dot.place(x=16, y=15)

        lbl = tk.Label(hdr, text="CC-MINI  |  Codex 一键切换",
                       font=("Segoe UI", 11, "bold"), fg=C["fg"], bg=C["panel"], pady=12)
        lbl.place(x=36, y=8)
        for w in (lbl,):
            w.bind("<ButtonPress-1>", self._ds)
            w.bind("<B1-Motion>",     self._dm)

        def wbtn(ch, cmd, hbg):
            b = tk.Label(hdr, text=ch, font=("Segoe UI", 10), fg=C["fg_dim"],
                         bg=C["panel"], width=3, cursor="hand2", pady=8)
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>",    lambda e: b.config(bg=hbg, fg=C["fg"]))
            b.bind("<Leave>",    lambda e: b.config(bg=C["panel"], fg=C["fg_dim"]))
            b.pack(side="right", ipady=4)
        wbtn("✕", self.destroy, "#c0392b")
        wbtn("—", self.iconify, C["border"])

        # 文档按钮（标题栏右侧，窗口控制左边）
        doc_btn = tk.Label(hdr, text=" 📖 文档 ", font=("Segoe UI", 9),
                           fg=C["teal"], bg=C["panel"], cursor="hand2", pady=8)
        doc_btn.pack(side="right", padx=(0, 4))
        doc_btn.bind("<Button-1>", lambda e: webbrowser.open("http://docs.h5.namawang.com/"))
        doc_btn.bind("<Enter>",    lambda e: doc_btn.config(fg="#fff", bg=C["teal"]))
        doc_btn.bind("<Leave>",    lambda e: doc_btn.config(fg=C["teal"], bg=C["panel"]))

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # 表单
        body = tk.Frame(self, bg=C["bg"], padx=32, pady=20)
        body.pack(fill="both", expand=True)

        cur_url, cur_key, cur_model = _read_current()

        # ── API 地址 ──
        self._field_label(body, "接口地址  (Base URL)")
        self.e_url = self._entry(body)
        self.e_url.insert(0, cur_url or DEFAULT_URL)

        # ── API Key + 获取按钮 ──
        self._field_label(body, "API 密钥  (API Key)")
        key_row = tk.Frame(body, bg=C["bg"])
        key_row.pack(fill="x", pady=(2, 10))

        key_wrap = tk.Frame(key_row, bg=C["inp_bdr"], padx=1, pady=1)
        key_wrap.pack(side="left", fill="x", expand=True)
        self.e_key = tk.Entry(key_wrap, font=("Consolas", 10), fg=C["fg"],
                              bg=C["inp"], insertbackground=C["fg"],
                              show="•", relief="flat", bd=0)
        self.e_key.pack(fill="x", ipady=7, ipadx=10)
        self.e_key.bind("<FocusIn>",  lambda e: key_wrap.config(bg=C["accent"]))
        self.e_key.bind("<FocusOut>", lambda e: key_wrap.config(bg=C["inp_bdr"]))
        if cur_key: self.e_key.insert(0, cur_key)

        # 获取按钮
        get_btn = tk.Label(key_row, text=" 获 取 ",
                           font=("Segoe UI", 9, "bold"),
                           fg=C["green"], bg=C["getbtn"],
                           padx=6, pady=6, cursor="hand2")
        get_btn.pack(side="left", padx=(8, 0))
        get_btn.bind("<Button-1>", lambda e: webbrowser.open(KEY_SITE))
        get_btn.bind("<Enter>",    lambda e: get_btn.config(bg="#2a5a3e"))
        get_btn.bind("<Leave>",    lambda e: get_btn.config(bg=C["getbtn"]))

        # ── 模型名称 ──
        self._field_label(body, "模型名称  (Model)")
        self.e_mdl = self._entry(body)
        self.e_mdl.insert(0, cur_model or "gpt-5.3-codex")
        self.e_mdl.bind("<Return>", lambda e: self._on_switch())

        # 快速选择 chips
        chips_row = tk.Frame(body, bg=C["bg"])
        chips_row.pack(fill="x", pady=(0, 6))
        for m in QUICK_MODELS:
            chip = tk.Label(chips_row, text=m, font=("Segoe UI", 8),
                            fg=C["fg_dim"], bg=C["chip"], padx=8, pady=3, cursor="hand2")
            chip.pack(side="left", padx=(0, 5))
            chip.bind("<Button-1>", lambda e, v=m: (
                self.e_mdl.delete(0, "end"), self.e_mdl.insert(0, v)))
            chip.bind("<Enter>", lambda e, w=chip: w.config(bg=C["chip_h"], fg=C["fg"]))
            chip.bind("<Leave>", lambda e, w=chip: w.config(bg=C["chip"], fg=C["fg_dim"]))

        # 状态文字
        self.sv = tk.StringVar()
        self.sl = tk.Label(body, textvariable=self.sv,
                           font=("Segoe UI", 8), fg=C["fg_mute"],
                           bg=C["bg"], anchor="w")
        self.sl.pack(fill="x", pady=(4, 0))

        # 底部切换按钮（全宽）
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        btn_c = tk.Canvas(self, height=62, bg=C["teal"],
                          highlightthickness=0, cursor="hand2")
        btn_c.pack(fill="x")

        def _draw_switch(hover=False):
            btn_c.delete("all")
            w = btn_c.winfo_width() or 500
            bg = C["teal_h"] if hover else C["teal"]
            btn_c.create_rectangle(0, 0, w, 62, fill=bg, outline="")
            btn_c.create_text(w//2, 24, text="⚡  立 即 切 换",
                              font=("Segoe UI", 14, "bold"), fill="#fff")
            btn_c.create_text(w//2, 46, text="APPLY CONFIG & API KEY",
                              font=("Segoe UI", 8), fill="#b2f5ea")

        btn_c.bind("<Button-1>", lambda e: self._on_switch())
        btn_c.bind("<Enter>",    lambda e: _draw_switch(True))
        btn_c.bind("<Leave>",    lambda e: _draw_switch(False))
        self.after(80, lambda: _draw_switch(False))

    def _field_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"),
                 fg=C["fg_dim"], bg=C["bg"], anchor="w"
                 ).pack(fill="x", pady=(0, 2))

    def _entry(self, parent):
        wrap = tk.Frame(parent, bg=C["inp_bdr"], padx=1, pady=1)
        wrap.pack(fill="x", pady=(0, 10))
        e = tk.Entry(wrap, font=("Consolas", 10), fg=C["fg"], bg=C["inp"],
                     insertbackground=C["fg"], relief="flat", bd=0)
        e.pack(fill="x", ipady=7, ipadx=10)
        e.bind("<FocusIn>",  lambda ev: wrap.config(bg=C["accent"]))
        e.bind("<FocusOut>", lambda ev: wrap.config(bg=C["inp_bdr"]))
        return e

    def _on_switch(self):
        url   = self.e_url.get().strip()
        key   = self.e_key.get().strip()
        model = self.e_mdl.get().strip()

        if not url:
            self._status("⚠  请填写接口地址", C["red"]); return
        if not url.startswith("http"):
            self._status("⚠  接口地址应以 http:// 或 https:// 开头", C["red"]); return
        if not key:
            self._status("⚠  请填写 API Key", C["red"])
            self.e_key.focus_set(); return
        if not model:
            self._status("⚠  请填写模型名称", C["red"])
            self.e_mdl.focus_set(); return

        err = do_switch(url, key, model)
        if err:
            self._status(f"✕  {err}", C["red"])
        else:
            self._status("✓  已保存，重启 Codex 后生效", C["green"])

    def _status(self, msg, color):
        self.sv.set(msg)
        self.sl.config(fg=color)


if __name__ == "__main__":
    App().mainloop()
