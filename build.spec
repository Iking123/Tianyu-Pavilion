# DeepSeekApp.spec
# 使用命令: pyinstaller DeepSeekApp.spec

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

# 应用名称和图标
app_name = "DeepSeekApp"
app_icon = "resources/icons/icon.ico"

# 添加所有资源文件和代码目录
added_files = [
    # 资源目录
    ("resources/icons", "resources/icons"),
    ("resources/images", "resources/images"),
    # 核心代码
    ("core", "core"),
    # 功能模块
    ("features/chat", "features/chat"),
    ("features/game", "features/game"),
    ("features/interactive_novel", "features/interactive_novel"),
    ("features/settings", "features/settings"),
    # UI模块
    ("ui", "ui"),
    # 单个文件
    ("funcs.py", "."),
]

# 分析主脚本
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        # PyQt5 相关
        "PyQt5",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "PyQt5.QtWebEngineWidgets",
        # Markdown 处理
        "markdown",
        "markdown.extensions",
        # 语法高亮
        "pygments",
        "pygments.styles",
        "pygments.lexers",
        # 其他可能的依赖
        "requests",
        "bs4",
        "lxml",
        "html2text",
        # 项目特定模块
        "core",
        "features",
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

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    icon=app_icon,  # 应用图标
    disable_windowed_tracker=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 收集所有文件
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
