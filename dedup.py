import os
import hashlib
import threading
import datetime
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
from send2trash import send2trash


# ============ 语言文本 ============
TEXTS = {
    "zh": {
        "title": "重复文件清理工具",
        "scan_dir": "扫描目录:",
        "browse": "浏览...",
        "start_scan": "开始扫描",
        "sort": "排序:",
        "sort_size": "文件大小",
        "sort_time": "创建时间",
        "order": "方向:",
        "order_desc": "从大到小",
        "order_asc": "从小到大",
        "per_page": "每页:",
        "prev_page": "◀ 上一页",
        "next_page": "下一页 ▶",
        "page_label": "第 {a} / {b} 页",
        "delete_checked": "删除勾选文件",
        "keep_oldest_page": "本页每组保留最早，勾选其余",
        "keep_newest_page": "本页每组保留最新，勾选其余",
        "keep_shortest_page": "本页每组保留最短路径，勾选其余",
        "clear_all": "全部取消勾选",
        "group_title": "第 {n} 组 — {c} 个相同文件 — 每个 {s}",
        "mtime": "修改",
        "ctime": "创建",
        "size": "大小",
        "copy": "复制",
        "menu_copy": "复制路径",
        "menu_open": "打开文件所在位置",
        "keep_oldest_group": "本组保留最早，勾选其余",
        "keep_newest_group": "本组保留最新，勾选其余",
        "clear_group": "本组全不选",
        "summary": "共 {groups} 组重复，{files} 个文件，可节省约 {size}　|　排序：{sort}（{order}）　|　本页显示第 {a}–{b} 组",
        "scanning": "正在扫描...",
        "hashing": "正在计算哈希 {a}/{b}...",
        "no_dup": "未发现重复文件",
        "please_choose": "请选择要扫描的文件夹",
        "choose_first": "请选择要扫描的文件夹",
        "no_checked": "当前没有勾选任何文件",
        "checked_info": "已勾选 {c} 个文件，共 {s}",
        "copied": "已复制路径：{p}",
        "opened": "已打开文件所在位置：{p}",
        "warn": "警告",
        "info": "提示",
        "error": "错误",
        "confirm_delete": "确认删除",
        "confirm_text": "即将把 {n} 个文件移到回收站，\n预计释放空间：{s}\n\n是否继续？",
        "group_all_checked": "第 {n} 组所有文件都被勾选，会导致该组文件全部被删除。\n请至少保留一个。",
        "no_check_del": "没有勾选任何文件",
        "done": "完成",
        "done_text": "成功移到回收站 {n} 个文件。\n已释放存储空间：{s}",
        "fail_list": "\n\n失败 {n} 个：\n{list}",
        "file_not_exist": "文件不存在或已被删除：\n{p}",
        "cannot_open": "无法打开文件夹：\n{e}",
        "lang": "语言Language:",
        "invalid_folder": "请选择有效的文件夹",
    },
    "en": {
        "title": "Duplicate File Cleaner",
        "scan_dir": "Folder:",
        "browse": "Browse...",
        "start_scan": "Scan",
        "sort": "Sort:",
        "sort_size": "File Size",
        "sort_time": "Created Time",
        "order": "Order:",
        "order_desc": "Descending",
        "order_asc": "Ascending",
        "per_page": "Per page:",
        "prev_page": "◀ Prev",
        "next_page": "Next ▶",
        "page_label": "Page {a} / {b}",
        "delete_checked": "Delete Checked",
        "keep_oldest_page": "Keep oldest in each group (this page)",
        "keep_newest_page": "Keep newest in each group (this page)",
        "keep_shortest_page": "Keep shortest path in each group (this page)",
        "clear_all": "Clear All Checks",
        "group_title": "Group {n} — {c} identical files — {s} each",
        "mtime": "Modified",
        "ctime": "Created",
        "size": "Size",
        "copy": "Copy",
        "menu_copy": "Copy Path",
        "menu_open": "Open File Location",
        "keep_oldest_group": "Keep oldest, check others",
        "keep_newest_group": "Keep newest, check others",
        "clear_group": "Uncheck all in group",
        "summary": "{groups} groups, {files} files, can save about {size}　|　Sort: {sort} ({order})　|　Showing {a}–{b}",
        "scanning": "Scanning...",
        "hashing": "Hashing {a}/{b}...",
        "no_dup": "No duplicate files found",
        "please_choose": "Please select a folder to scan",
        "choose_first": "Please select a folder to scan",
        "no_checked": "No files checked",
        "checked_info": "Checked {c} files, total {s}",
        "copied": "Copied: {p}",
        "opened": "Opened location: {p}",
        "warn": "Warning",
        "info": "Info",
        "error": "Error",
        "confirm_delete": "Confirm Delete",
        "confirm_text": "Move {n} files to Recycle Bin?\nEstimated space freed: {s}\n\nContinue?",
        "group_all_checked": "All files in group {n} are checked. At least one must be kept.",
        "no_check_del": "No files checked",
        "done": "Done",
        "done_text": "Moved {n} files to Recycle Bin.\nSpace freed: {s}",
        "fail_list": "\n\n{n} failed:\n{list}",
        "file_not_exist": "File not found or already deleted:\n{p}",
        "cannot_open": "Cannot open folder:\n{e}",
        "lang": "Language语言:",
        "invalid_folder": "Please select a valid folder",
    },
}

LANG_DISPLAY = {"中文": "zh", "English": "en"}
LANG_DISPLAY_REVERSE = {"zh": "中文", "en": "English"}


class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.lang = "zh"  # 当前语言

        self.folder = tk.StringVar()
        self.summary = tk.StringVar()
        self.checked_info = tk.StringVar()
        self.sort_key = tk.StringVar()
        self.sort_order = tk.StringVar()
        self.page_size = tk.IntVar(value=50)
        self.page_no = tk.IntVar(value=1)
        self.page_label = tk.StringVar()
        self.lang_display = tk.StringVar(value="中文")

        self.groups = []
        self.sorted_groups = []
        self.check_vars = {}
        self.selected_paths = set()

        # 保存会被翻译的控件引用，切换语言时刷新
        self._widgets = {}

        self._build_ui()
        self._apply_lang()

    def t(self, key, **kw):
        """取当前语言的文本"""
        s = TEXTS[self.lang].get(key, key)
        if kw:
            try:
                s = s.format(**kw)
            except Exception:
                pass
        return s

    # ---------- UI ----------
    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        self._widgets["scan_dir"] = ttk.Label(top, text="")
        self._widgets["scan_dir"].pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.folder).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self._widgets["browse"] = ttk.Button(top, text="", command=self.choose_folder)
        self._widgets["browse"].pack(side=tk.LEFT)
        self._widgets["start_scan"] = ttk.Button(top, text="", command=self.start_scan)
        self._widgets["start_scan"].pack(side=tk.LEFT, padx=5)

        # 语言选择
        self._widgets["lang"] = ttk.Label(top, text="")
        self._widgets["lang"].pack(side=tk.LEFT, padx=(10, 2))
        lang_box = ttk.Combobox(top, textvariable=self.lang_display,
                                values=["中文", "English"],
                                state="readonly", width=8)
        lang_box.pack(side=tk.LEFT)
        lang_box.bind("<<ComboboxSelected>>", lambda e: self._switch_lang())

        ctrl = ttk.Frame(self.root, padding=(8, 0))
        ctrl.pack(fill=tk.X)

        self._widgets["sort"] = ttk.Label(ctrl, text="")
        self._widgets["sort"].pack(side=tk.LEFT)
        self.sort_key_box = ttk.Combobox(ctrl, textvariable=self.sort_key,
                                         state="readonly", width=10)
        self.sort_key_box.pack(side=tk.LEFT, padx=3)
        self.sort_key_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_sort())

        self.sort_order_box = ttk.Combobox(ctrl, textvariable=self.sort_order,
                                           state="readonly", width=10)
        self.sort_order_box.pack(side=tk.LEFT, padx=3)
        self.sort_order_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_sort())

        ttk.Separator(ctrl, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        self._widgets["per_page"] = ttk.Label(ctrl, text="")
        self._widgets["per_page"].pack(side=tk.LEFT)
        size_box = ttk.Combobox(ctrl, textvariable=self.page_size,
                                values=[20, 50, 100, 200],
                                state="readonly", width=5)
        size_box.pack(side=tk.LEFT, padx=3)
        size_box.bind("<<ComboboxSelected>>", lambda e: self._on_page_size_change())

        self._widgets["prev_page"] = ttk.Button(ctrl, text="", command=self.prev_page)
        self._widgets["prev_page"].pack(side=tk.LEFT, padx=3)
        ttk.Label(ctrl, textvariable=self.page_label).pack(side=tk.LEFT, padx=3)
        self._widgets["next_page"] = ttk.Button(ctrl, text="", command=self.next_page)
        self._widgets["next_page"].pack(side=tk.LEFT, padx=3)

        ops = ttk.Frame(self.root, padding=(8, 4))
        ops.pack(fill=tk.X)
        self._widgets["delete_checked"] = ttk.Button(
            ops, text="", command=self.delete_checked)
        self._widgets["delete_checked"].pack(side=tk.LEFT)
        self._widgets["keep_oldest_page"] = ttk.Button(
            ops, text="", command=lambda: self.auto_check("oldest"))
        self._widgets["keep_oldest_page"].pack(side=tk.LEFT, padx=5)
        self._widgets["keep_newest_page"] = ttk.Button(
            ops, text="", command=lambda: self.auto_check("newest"))
        self._widgets["keep_newest_page"].pack(side=tk.LEFT, padx=5)
        self._widgets["keep_shortest_page"] = ttk.Button(
            ops, text="", command=lambda: self.auto_check("shortest"))
        self._widgets["keep_shortest_page"].pack(side=tk.LEFT, padx=5)
        self._widgets["clear_all"] = ttk.Button(
            ops, text="", command=self.clear_checks)
        self._widgets["clear_all"].pack(side=tk.LEFT, padx=5)

        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(-e.delta // 120, "units"))

        ttk.Label(self.root, textvariable=self.summary,
                  relief=tk.SUNKEN, anchor=tk.W,
                  padding=(6, 2)).pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(self.root, textvariable=self.checked_info,
                  relief=tk.SUNKEN, anchor=tk.W,
                  padding=(6, 2)).pack(fill=tk.X, side=tk.BOTTOM)

    def _apply_lang(self):
        """把当前语言应用到所有静态控件"""
        self.root.title(self.t("title"))
        for key, w in self._widgets.items():
            try:
                w.config(text=self.t(key))
            except Exception:
                pass

        # 排序下拉的选项文字
        self.sort_key_box.config(values=[self.t("sort_size"), self.t("sort_time")])
        self.sort_order_box.config(values=[self.t("order_desc"), self.t("order_asc")])

        # 恢复排序值（切换语言后，值也变文字了）
        cur_key = self.sort_key.get()
        if cur_key in (TEXTS["zh"]["sort_size"], TEXTS["en"]["sort_size"], ""):
            self.sort_key.set(self.t("sort_size"))
        else:
            self.sort_key.set(self.t("sort_time"))

        cur_order = self.sort_order.get()
        if cur_order in (TEXTS["zh"]["order_desc"], TEXTS["en"]["order_desc"], ""):
            self.sort_order.set(self.t("order_desc"))
        else:
            self.sort_order.set(self.t("order_asc"))

        # 恢复状态栏文字
        if not self.groups:
            self.summary.set(self.t("please_choose"))
        if not self.selected_paths:
            self.checked_info.set(self.t("no_checked"))

        # 重新渲染结果（翻译组标题、按钮等）
        if self.sorted_groups:
            self.render_page()

    def _switch_lang(self):
        self.lang = LANG_DISPLAY.get(self.lang_display.get(), "zh")
        self._apply_lang()

    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder.set(path)

    # ---------- 扫描 ----------
    def start_scan(self):
        folder = self.folder.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning(self.t("info"), self.t("invalid_folder"))
            return
        self.summary.set(self.t("scanning"))
        self._clear_results()
        threading.Thread(target=self._scan_worker, args=(folder,), daemon=True).start()

    def _scan_worker(self, folder):
        size_map = defaultdict(list)
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for name in filenames:
                if name.startswith('.'):
                    continue
                fp = os.path.join(dirpath, name)
                try:
                    if os.path.islink(fp) or not os.path.isfile(fp):
                        continue
                    size = os.path.getsize(fp)
                    if size == 0:
                        continue
                    size_map[size].append(fp)
                except OSError:
                    continue

        hash_map = defaultdict(list)
        candidates = [f for files in size_map.values() if len(files) > 1 for f in files]
        total = len(candidates)
        done = 0
        for fp in candidates:
            h = self._file_hash(fp)
            if h:
                hash_map[h].append(fp)
            done += 1
            if done % 20 == 0:
                self.root.after(0, self.summary.set,
                                self.t("hashing", a=done, b=total))

        groups = []
        for h, files in hash_map.items():
            if len(files) > 1:
                items = []
                for fp in files:
                    try:
                        st = os.stat(fp)
                        items.append({
                            "path": fp,
                            "size": st.st_size,
                            "mtime": st.st_mtime,
                            "ctime": st.st_ctime,
                        })
                    except OSError:
                        continue
                if len(items) > 1:
                    groups.append(items)

        self.root.after(0, self._on_scan_done, groups)

    def _file_hash(self, path, chunk_size=1 << 20):
        h = hashlib.sha1()
        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()
        except OSError:
            return None

    def _on_scan_done(self, groups):
        self.groups = groups
        self.selected_paths.clear()
        self.checked_info.set(self.t("no_checked"))
        if not groups:
            self._clear_results()
            self.summary.set(self.t("no_dup"))
            return
        self.page_no.set(1)
        self.refresh_sort()

    # ---------- 排序 / 分页 ----------
    def _sorted_groups(self):
        by_size = (self.sort_key.get() == self.t("sort_size"))
        desc = (self.sort_order.get() == self.t("order_desc"))

        def key_func(item):
            return item["size"] if by_size else item["ctime"]

        groups = [g[:] for g in self.groups]
        for g in groups:
            g.sort(key=key_func, reverse=desc)
        groups.sort(key=lambda g: key_func(g[0]), reverse=desc)
        return groups

    def total_pages(self):
        if not self.sorted_groups:
            return 1
        n = len(self.sorted_groups)
        ps = max(1, self.page_size.get())
        return (n + ps - 1) // ps

    def _on_page_size_change(self):
        self.page_no.set(1)
        if self.sorted_groups:
            self.render_page()

    def prev_page(self):
        if self.page_no.get() > 1:
            self.page_no.set(self.page_no.get() - 1)
            self.render_page()

    def next_page(self):
        if self.page_no.get() < self.total_pages():
            self.page_no.set(self.page_no.get() + 1)
            self.render_page()

    def refresh_sort(self):
        if not self.groups:
            return
        self._save_checks()
        self.sorted_groups = self._sorted_groups()
        self.page_no.set(1)
        self.render_page()

    def render_page(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.check_vars.clear()

        if not self.sorted_groups:
            self.page_label.set(self.t("page_label", a=1, b=1))
            return

        total = len(self.sorted_groups)
        ps = max(1, self.page_size.get())
        tp = self.total_pages()
        pn = min(max(1, self.page_no.get()), tp)
        self.page_no.set(pn)

        start = (pn - 1) * ps
        end = min(start + ps, total)
        page_groups = self.sorted_groups[start:end]

        self.page_label.set(self.t("page_label", a=pn, b=tp))

        total_files = sum(len(g) for g in self.sorted_groups)
        total_wasted = sum((len(g) - 1) * g[0]["size"] for g in self.sorted_groups)
        self.summary.set(self.t(
            "summary",
            groups=total, files=total_files,
            size=self._human(total_wasted),
            sort=self.sort_key.get(), order=self.sort_order.get(),
            a=start + 1, b=end))

        for local_i, group in enumerate(page_groups):
            abs_gi = start + local_i
            frame = ttk.LabelFrame(
                self.scroll_frame,
                text=self.t("group_title", n=abs_gi + 1,
                            c=len(group),
                            s=self._human(group[0]['size'])),
                padding=6)
            frame.pack(fill=tk.X, expand=True, padx=4, pady=4)

            for fi, item in enumerate(group):
                row = ttk.Frame(frame)
                row.pack(fill=tk.X, pady=1)

                var = tk.BooleanVar(value=(item["path"] in self.selected_paths))
                self.check_vars[(abs_gi, fi)] = var
                cb = ttk.Checkbutton(row, variable=var,
                                     command=self._update_checked_info)
                cb.pack(side=tk.LEFT)

                mtime = datetime.datetime.fromtimestamp(item["mtime"]).strftime(
                    "%Y-%m-%d %H:%M:%S")
                ctime = datetime.datetime.fromtimestamp(item["ctime"]).strftime(
                    "%Y-%m-%d %H:%M:%S")
                text = (f"{item['path']}\n"
                        f"      {self.t('mtime')}: {mtime}　"
                        f"{self.t('ctime')}: {ctime}　"
                        f"{self.t('size')}: {self._human(item['size'])}")
                lbl = ttk.Label(row, text=text, anchor=tk.W, justify=tk.LEFT)
                lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

                path = item["path"]

                lbl.bind("<Double-Button-1>",
                         lambda e, p=path: self._open_in_explorer(p))

                def _make_menu(p=path):
                    m = tk.Menu(self.root, tearoff=0)
                    m.add_command(label=self.t("menu_copy"),
                                  command=lambda: self._copy_path(p))
                    m.add_command(label=self.t("menu_open"),
                                  command=lambda: self._open_in_explorer(p))
                    return m

                lbl.bind("<Button-3>",
                         lambda e, p=path: _make_menu(p).tk_popup(e.x_root, e.y_root))

                ttk.Button(row, text=self.t("copy"), width=6,
                           command=lambda p=path: self._copy_path(p)
                           ).pack(side=tk.RIGHT, padx=2)

            btn_row = ttk.Frame(frame)
            btn_row.pack(fill=tk.X, pady=(4, 0))
            ttk.Button(btn_row, text=self.t("keep_oldest_group"),
                       command=lambda g=abs_gi: self._group_auto_check(g, "oldest")
                       ).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_row, text=self.t("keep_newest_group"),
                       command=lambda g=abs_gi: self._group_auto_check(g, "newest")
                       ).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_row, text=self.t("clear_group"),
                       command=lambda g=abs_gi: self._group_clear(g)
                       ).pack(side=tk.LEFT, padx=2)

        self.canvas.yview_moveto(0)

    def _save_checks(self):
        for (gi, fi), var in self.check_vars.items():
            if gi < len(self.sorted_groups) and fi < len(self.sorted_groups[gi]):
                path = self.sorted_groups[gi][fi]["path"]
                if var.get():
                    self.selected_paths.add(path)
                else:
                    self.selected_paths.discard(path)

    def _clear_results(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.check_vars.clear()
        self.groups = []
        self.sorted_groups = []
        self.selected_paths.clear()
        self.page_label.set(self.t("page_label", a=1, b=1))
        self.checked_info.set(self.t("no_checked"))

    def _human(self, n):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024:
                return f"{n:.1f}{unit}"
            n /= 1024
        return f"{n:.1f}PB"

    # ---------- 勾选统计 ----------
    def _checked_size(self):
        total_size = 0
        count = 0
        for group in self.sorted_groups:
            for item in group:
                if item["path"] in self.selected_paths:
                    total_size += item["size"]
                    count += 1
        return count, total_size

    def _update_checked_info(self):
        self._save_checks()
        count, size = self._checked_size()
        if count == 0:
            self.checked_info.set(self.t("no_checked"))
        else:
            self.checked_info.set(
                self.t("checked_info", c=count, s=self._human(size)))

    # ---------- 复制 / 打开文件夹 ----------
    def _copy_path(self, path):
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self.root.update()
        self.checked_info.set(self.t("copied", p=path))

    def _open_in_explorer(self, path):
        clean = path
        if clean.startswith("\\\\?\\"):
            clean = clean[4:]

        if not os.path.exists(clean):
            messagebox.showwarning(self.t("info"),
                                   self.t("file_not_exist", p=clean))
            return

        try:
            subprocess.Popen(["explorer", "/select,", os.path.normpath(clean)])
            self.checked_info.set(self.t("opened", p=clean))
        except Exception as e:
            messagebox.showerror(self.t("error"),
                                 self.t("cannot_open", e=e))

    # ---------- 勾选逻辑 ----------
    def auto_check(self, mode):
        ps = max(1, self.page_size.get())
        pn = self.page_no.get()
        start = (pn - 1) * ps
        end = min(start + ps, len(self.sorted_groups))
        for gi in range(start, end):
            self._group_auto_check(gi, mode)

    def _group_auto_check(self, gi, mode):
        group = self.sorted_groups[gi]
        if not group:
            return
        if mode == "oldest":
            keep = min(range(len(group)), key=lambda i: group[i]["mtime"])
        elif mode == "newest":
            keep = max(range(len(group)), key=lambda i: group[i]["mtime"])
        elif mode == "shortest":
            keep = min(range(len(group)), key=lambda i: len(group[i]["path"]))
        else:
            return
        for fi in range(len(group)):
            var = self.check_vars.get((gi, fi))
            if var is not None:
                var.set(fi != keep)
        self._save_checks()
        self._update_checked_info()

    def _group_clear(self, gi):
        for fi in range(len(self.sorted_groups[gi])):
            var = self.check_vars.get((gi, fi))
            if var is not None:
                var.set(False)
        self._save_checks()
        self._update_checked_info()

    def clear_checks(self):
        for var in self.check_vars.values():
            var.set(False)
        self.selected_paths.clear()
        self._update_checked_info()

    # ---------- 删除 ----------
    def delete_checked(self):
        self._save_checks()

        if not self.selected_paths:
            messagebox.showinfo(self.t("info"), self.t("no_check_del"))
            return

        for gi, group in enumerate(self.sorted_groups):
            all_paths = {it["path"] for it in group}
            if all_paths and all_paths.issubset(self.selected_paths):
                messagebox.showwarning(
                    self.t("warn"),
                    self.t("group_all_checked", n=gi + 1))
                return

        to_delete = list(self.selected_paths)
        freed_size = 0
        for group in self.sorted_groups:
            for item in group:
                if item["path"] in self.selected_paths:
                    freed_size += item["size"]

        if not messagebox.askyesno(
                self.t("confirm_delete"),
                self.t("confirm_text", n=len(to_delete),
                       s=self._human(freed_size))):
            return

        ok, fail = 0, []
        for fp in to_delete:
            try:
                clean = fp
                if clean.startswith("\\\\?\\"):
                    clean = clean[4:]
                send2trash(clean)
                ok += 1
            except Exception as e:
                try:
                    import ctypes
                    from ctypes import wintypes
                    FO_DELETE = 3
                    FOF_ALLOWUNDO = 0x0040
                    FOF_NOCONFIRMATION = 0x0010
                    FOF_SILENT = 0x0004

                    class SHFILEOPSTRUCTW(ctypes.Structure):
                        _fields_ = [
                            ("hwnd", wintypes.HWND),
                            ("wFunc", wintypes.UINT),
                            ("pFrom", wintypes.LPCWSTR),
                            ("pTo", wintypes.LPCWSTR),
                            ("fFlags", ctypes.c_uint16),
                            ("fAnyOperationsAborted", wintypes.BOOL),
                            ("hNameMappings", ctypes.c_void_p),
                            ("lpszProgressTitle", wintypes.LPCWSTR),
                        ]

                    op = SHFILEOPSTRUCTW()
                    op.wFunc = FO_DELETE
                    op.pFrom = clean + "\0\0"
                    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
                    res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
                    if res == 0:
                        ok += 1
                    else:
                        fail.append(f"{fp}: {res}")
                except Exception as e2:
                    fail.append(f"{fp}: {e} / {e2}")

        freed_ok = 0
        for group in self.sorted_groups:
            for item in group:
                if item["path"] in self.selected_paths:
                    p = item["path"]
                    if p.startswith("\\\\?\\"):
                        p = p[4:]
                    if not os.path.exists(p):
                        freed_ok += item["size"]

        msg = self.t("done_text", n=ok, s=self._human(freed_ok))
        if fail:
            msg += self.t("fail_list", n=len(fail),
                          list="\n".join(fail[:10]))
        messagebox.showinfo(self.t("done"), msg)

        self.selected_paths.clear()
        self.start_scan()


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()