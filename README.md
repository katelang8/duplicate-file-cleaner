# Duplicate File Cleaner / 重复文件清理工具

A graphical tool for Windows to find and clean duplicate files.
Finding is based on file content, not just file name. Deleted files are moved to the Recycle Bin, so they can be restored.

一款 Windows 平台的图形化重复文件清理工具。
按文件内容查找重复文件（不只看文件名），删除时移到回收站，可随时还原。

---

## Features / 功能

- Find duplicate files by content (SHA1 hash) / 按文件内容查找重复文件
- Sort by file size or created time / 支持按文件大小、创建时间排序
- Pagination for large result sets / 分页显示，支持大量重复文件
- Move to Recycle Bin instead of permanent delete / 删除时移到回收站，可还原
- Copy file path / 路径可一键复制
- Double-click to open file location / 双击路径打开所在文件夹
- Chinese / English bilingual interface / 中英文双语界面

## Download / 下载

Download `DuplicateFileCleaner.exe` from this repository and double-click to run.
No installation required.

在本仓库下载 `DuplicateFileCleaner.exe`，双击即可运行，无需安装。

Detailed instructions: see `Duplicate File Cleaner   User Manual.txt` in this repository.
详细使用方法：见仓库中的 `Duplicate File Cleaner   User Manual.txt`。

## Tech Stack / 技术栈

- Python 3.9
- tkinter (GUI)
- send2trash (Recycle Bin support)
- PyInstaller (packaging)

## Platform / 适用平台

Windows only / 仅支持 Windows

## License / 许可证

MIT License
