# build.spec
# 使用命令: pyinstaller build.spec

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import sys

block_cipher = None

# 应用名称和图标
app_name = "天语阁"
app_icon = "resources/icons/icon.ico"

# 添加所有资源文件和代码目录
added_files = [
    # 资源目录 - 包含所有子目录
    ("resources", "resources"),
    # 核心代码
    ("core", "core"),
    # 功能模块
    ("features/chat", "features/chat"),
    ("features/game", "features/game"),
    ("features/interactive_novel", "features/interactive_novel"),
    ("features/settings", "features/settings"),
    ("features/character", "features/character"),
    ("features/creative_writing", "features/creative_writing"),
    # UI模块
    ("ui", "ui"),
    # 单个文件
    ("funcs.py", "."),
    ("translate.py", "."),
]

# 分析主脚本
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        # PyQt6 相关
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtNetwork",
        # Markdown 处理
        "markdown",
        "markdown.extensions",
        # 语法高亮
        "pygments",
        "pygments.styles",
        "pygments.lexers",
        # 其他依赖
        "requests",
        "bs4",
        "lxml",
        "html2text",
        "jieba",
        # 项目特定模块
        "core",
        "features",
        "features.character",
        "features.chat",
        "features.creative_writing",
        "features.game",
        "features.interactive_novel",
        "features.settings",
        "ui",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 可执行文件配置（仅作为文件夹内的exe，不单独生成）
exe = EXE(
    pyz,
    a.scripts,
    [],  # 移除 a.binaries/a.zipfiles/a.datas，交给COLLECT处理
    exclude_binaries=True,  # 关键：排除二进制文件，让COLLECT统一管理
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=app_icon,
    disable_windowed_tracker=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 收集所有文件到文件夹（核心：只生成文件夹）
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
