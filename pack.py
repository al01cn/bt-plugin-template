#!/usr/bin/env python
# coding: utf-8
"""
宝塔插件打包脚本

用法:
    python pack.py                # 默认打包
    python pack.py --version 1.1  # 指定版本号打包

流程:
    1. 从 package.json 读取插件信息
    2. 读取 src/ 源码，替换占位符 {{#key#}}
    3. 生成 info.json（从 package.json 直接构建）
    4. 打包到 dist/zip，不修改 src/ 任何文件

占位符语法: {{#字段名#}}，字段名对应 package.json 中的键。
src/ 中任何文件都可以使用占位符，打包时自动替换（仅在文件包含占位符时才处理）。
代码文件（JS/Python）中建议写成 "{{#key#}}" 字符串形式，避免触发代码审查。
templates/ 目录不参与替换（保留 Jinja2 模板语法）。
"""

import os
import sys
import re
import json
import shutil
import zipfile
import argparse

# 占位符正则: {{#字段名#}}
PLACEHOLDER_RE = re.compile(r"\{\{#(\w+)#\}\}")


def load_package_json():
    """从根目录 package.json 读取插件信息"""
    pkg_path = os.path.join(BASE_DIR, "package.json")
    if not os.path.exists(pkg_path):
        print("[错误] 找不到根目录 package.json")
        sys.exit(1)

    with open(pkg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def has_placeholder(content):
    """检查内容是否包含占位符"""
    return PLACEHOLDER_RE.search(content) is not None


def replace_placeholders(content, variables):
    """替换内容中的 {{#key#}} 占位符，未匹配到的保持原样"""
    def replacer(match):
        key = match.group(1)
        if key in variables:
            return str(variables[key])
        return match.group(0)

    return PLACEHOLDER_RE.sub(replacer, content)


def build_info_json(variables):
    """构建 info.json 内容（从 package.json 提取宝塔需要的字段）"""
    bt_fields = ["title", "name", "ps", "versions", "checks", "author", "home", "sort", "icon", "coexist"]
    info = {}
    for field in bt_fields:
        if field in variables:
            info[field] = variables[field]
    return info


def clear_dist():
    """清空 dist 目录"""
    if os.path.exists(DIST_DIR):
        for item in os.listdir(DIST_DIR):
            item_path = os.path.join(DIST_DIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    else:
        os.makedirs(DIST_DIR)
    print("[信息] 已清理 dist 目录")


# 不打包的文件/目录
EXCLUDE_NAMES = {".git", ".gitignore", "__pycache__", ".DS_Store", "Thumbs.db"}
EXCLUDE_EXTS = {".pyc", ".pyo"}


def should_exclude(name):
    """判断文件是否应该排除"""
    if name in EXCLUDE_NAMES:
        return True
    for ext in EXCLUDE_EXTS:
        if name.endswith(ext):
            return True
    return False


def pack(args):
    """执行打包"""
    # 1. 从 package.json 读取信息
    pkg_info = load_package_json()

    # 2. 构建替换变量
    variables = dict(pkg_info)
    if args.version:
        variables["versions"] = args.version

    plugin_name = variables.get("name", "demo")
    version = variables.get("versions", "1.0")

    print(f"[打包] 插件名称: {plugin_name}")
    print(f"[打包] 版本号: {version}")
    print("=" * 40)

    # 3. 清理 dist
    clear_dist()

    # 4. 打包 src/ 源码，替换占位符后写入 zip
    zip_name = f"{plugin_name}_v{version}.zip"
    zip_path = os.path.join(DIST_DIR, zip_name)

    # templates/ 目录不替换占位符
    NO_REPLACE_PREFIX = os.path.join(SRC_DIR, "templates")

    print("-" * 40)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        file_count = 0
        for root, dirs, files in os.walk(SRC_DIR):
            dirs[:] = [d for d in dirs if not should_exclude(d)]

            for file in files:
                if should_exclude(file):
                    continue

                src_path = os.path.join(root, file)
                arc_name = os.path.relpath(src_path, SRC_DIR).replace("\\", "/")

                # 判断是否需要替换占位符
                if root.startswith(NO_REPLACE_PREFIX):
                    # templates/ 不替换，原样写入
                    zf.write(src_path, arc_name)
                else:
                    # 其他源码文件：读取 → 仅当包含占位符时替换 → 写入 zip
                    try:
                        with open(src_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except (UnicodeDecodeError, PermissionError):
                        # 二进制文件原样写入
                        zf.write(src_path, arc_name)
                    else:
                        if has_placeholder(content):
                            content = replace_placeholders(content, variables)
                            zf.writestr(arc_name, content)
                        else:
                            # 无占位符，原样写入（不经过字符串处理）
                            zf.write(src_path, arc_name)

                file_count += 1
                print(f"  + {arc_name}")

        # 写入 info.json（从 package.json 构建，不依赖源码文件）
        info = build_info_json(variables)
        zf.writestr("info.json", json.dumps(info, ensure_ascii=False, indent=2) + "\n")
        file_count += 1
        print("  + info.json")

    size = os.path.getsize(zip_path)
    size_str = f"{size / (1024 * 1024):.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"

    print("-" * 40)
    print(f"[完成] 共打包 {file_count} 个文件")
    print(f"[完成] 输出: dist/{zip_name} ({size_str})")


# ===== 路径配置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
DIST_DIR = os.path.join(BASE_DIR, "dist")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="宝塔插件打包工具")
    parser.add_argument("--version", "-v", type=str, default=None, help="指定版本号（默认读取 package.json）")
    pack(parser.parse_args())
