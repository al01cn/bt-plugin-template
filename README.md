# 宝塔面板插件 DEMO

一个最小化的宝塔 Linux 面板第三方插件模板，用于快速开始插件开发。

## 项目结构

```
demo/
├── package.json                    # 插件信息（统一管理，修改这里即可）
├── build                           # Linux/macOS 打包脚本 (./build)
├── build.sh                        # Linux/Unix 打包脚本 (./build.sh)
├── build.bat                       # Windows 批处理脚本
├── build.ps1                       # Windows PowerShell 脚本
├── src/                            # 源码目录（也是插件的实际目录结构）
│   ├── info.json                   # 由 pack.py 自动生成，不入 git
│   ├── install.sh                  # 安装脚本（支持占位符替换）
│   ├── icon.png                    # 插件图标（建议 32x32 PNG）
│   ├── index.html                  # 前端面板页面（宝塔内嵌渲染）
│   ├── {{#plugin_name#}}_main.py   # 后端主程序（打包时自动重命名为 {name}_main.py）
│   └── static/
│       └── js/
│           ├── package.js          # 前端配置（支持占位符替换，如 {{#plugin_name#}} → demo），为了方便你获取到配置信息，所以进行了这样的处理。
│           └── main.js             # 前端交互脚本（从 window.__BT_PLUGIN__ 读取信息）
├── dist/                           # 打包输出（自动生成，不要手动修改）
├── pack.py                         # 打包脚本
├── .gitignore
└── README.md
```

## 设计思路

**核心原则：占位符直观可读，打包时自动替换。**

- 插件信息集中在根目录 `package.json` 管理，打包时自动替换源码中的占位符并生成：
  - `src/info.json` — 宝塔插件配置
- 占位符语法 `{{#plugin_xxx#}}`，以 `plugin_` 前缀命名，开发者一眼就能看懂含义
- 占位符与 `package.json` 字段的映射关系定义在 `pack.py` 的 `PLACEHOLDER_MAP` 中
- `templates/` 目录不参与占位符替换（保留 Jinja2 原生 `{{ }}` 语法）

## 开发调试

> ⚠️ **重要提示**：宝塔面板没有提供热重载功能，每次修改代码后都需要重新打包并上传安装。

### 开启开发者模式

1. 登录宝塔面板
2. 进入 **面板设置** → **开发者选项** → 打开开关
3. 进入 **软件商店** → **第三方应用**
4. 点击 **导入插件**，选择打包好的 zip 文件进行安装

### 调试流程

```bash
# 1. 修改代码
# 编辑 src/ 目录下的文件

# 2. 打包插件（开发版）
./build                    # Linux/macOS
build.bat                  # Windows CMD
.\build.ps1                # Windows PowerShell

# 3. 上传到服务器
scp dist/dev/demo_vdev_1.0.zip root@your-server:/tmp/

# 4. 在宝塔面板中导入安装
# 软件商店 → 第三方应用 → 导入插件 → 选择 /tmp/demo_vdev_1.0.zip

# 5. 测试功能，重复上述步骤
```

## 快速开始

### 1. 修改插件信息

编辑根目录的 `package.json`（**唯一的信息管理入口**）：

```json
{
  "title": "你的插件名称",
  "name": "your_plugin",       // 必须与目录名一致
  "ps": "插件功能描述",
  "versions": "1.0",
  "author": "你的名字",
  "home": "https://your-site.com",
  "sort": 100,
  "icon": "icon.png",
  "coexist": true
}
```

### 2. 修改主程序类名

在 `src/{{#plugin_name#}}_main.py` 中，将类名改为 `plugin_name_main`。打包时会自动替换为 `{name}_main`。

例如：如果 `package.json` 中 `"name": "myplugin"`，则：
- 文件名：`{{#plugin_name#}}_main.py` → 打包后变为 `myplugin_main.py`
- 类名：`class plugin_name_main:` → 打包后变为 `class myplugin_main:`

**注意：** 使用 `plugin_name_main` 作为类名可以避免开发时的语法检查错误。

### 3. 开发后端 API

在 `_main.py` 中添加方法即可暴露为 API：

```python
class your_plugin_main:
    def your_method(self, args):
        # args 是前端传来的参数字典
        return {"key": "value"}  # 自动序列化为 JSON
```

### 4. 打包

#### 快捷打包（推荐）

**Linux/macOS:**
```bash
chmod +x build              # 首次添加执行权限
./build                     # 默认开发版
./build -t beta             # 测试版
./build -t release          # 正式版
./build -v 2.0 -t beta      # 指定版本+类型
./build -h                  # 查看帮助
```

**Windows CMD:**
```cmd
build.bat -t dev
build.bat -t beta
build.bat -v 2.0 -t release
```

**Windows PowerShell:**
```powershell
.\build.ps1 -t dev
.\build.ps1 -t beta
.\build.ps1 -v 2.0 -t release
```

#### 直接使用 Python

```bash
python pack.py                          # 默认开发版
python pack.py --type beta              # 测试版
python pack.py --type release           # 正式版
python pack.py -v 2.0 -t beta           # 指定版本+类型
python pack.py --help                   # 查看帮助
```

#### 构建类型说明

| 类型 | 输出目录 | 压缩包名 | 标题后缀 | is_beta |
|------|---------|---------|---------|--------|
| `dev` (默认) | `dist/dev/` | `demo_vdev_1.0.zip` | `[开发版]` | ✅ true |
| `beta` | `dist/beta/` | `demo_vbeta_1.0.zip` | `[测试版]` | ✅ true |
| `release` | `dist/release/` | `demo_v1.0.zip` | 无 | ❌ 无 |

**参数说明：**
- `-t, --type`: 构建类型 (dev/beta/release)，默认为 dev
- `-v, --version`: 指定版本号，覆盖 package.json 中的版本
- `-h, --help`: 显示帮助信息

#### 打包流程

1. 读取 `package.json` 获取插件信息
2. 根据构建类型调整配置（标题、is_beta 字段等）
3. 遍历 `src/` 文件，替换 `{{#plugin_xxx#}}` 占位符
4. 生成 `info.json`（包含宝塔需要的配置）
5. 打包为 zip 文件到对应目录

### 5. 安装到宝塔面板

将 `dist/` 目录下的 zip 文件上传到宝塔面板，通过第三方插件导入安装。

或手动安装：

```bash
scp -r src/* root@your-server:/www/server/panel/plugin/demo/
bash /www/server/panel/plugin/demo/install.sh install
```

## API 接口说明

| 方法 | 说明 | 参数 |
|------|------|------|
| `index` | 插件首页数据 | - |
| `get_system_info` | 获取系统信息 | - |
| `get_disk_info` | 获取磁盘信息 | - |
| `ping` | 心跳测试 | `msg` (可选) |
| `echo` | 数据回显 | 任意参数 |
| `test_error` | 模拟错误返回 | - |

## 宝塔 public 模块常用方法

```python
import public

# 返回标准消息格式
public.returnMsg(True, "成功信息")
public.returnMsg(False, "错误信息")

# 写入日志
public.WriteLog("插件名称", "日志内容")

# 执行系统命令
result, err = public.ExecShell("ls -la")

# 读取/写入文件
content = public.readFile("/path/to/file")
public.writeFile("/path/to/file", "内容")
```

## 注意事项

- 后端方法返回值只支持 `bool`、`str`、`list`、`dict`、`int`，不要返回其他类型
- 避免使用 `action`、`name`、`s`、`a` 等保留字段作为参数名
- 前端页面在宝塔面板 iframe 内渲染，不要写完整的 HTML 结构（`<!DOCTYPE>` 等），只写内容片段
- `templates/index.html` 是独立模板页面，需要完整的 HTML 结构
- `{{#plugin_name#}}_main.py` 文件在开发时会有语法警告，这是正常的，打包时会自动重命名

## VSCode 代码片段

项目内置了 `.vscode/*.code-snippets`，在对应文件类型中输入前缀即可 Tab 补全：

| 前缀 | 文件类型 | 作用 |
|------|----------|------|
| `bt-package` | JS / JSON | 生成 `package.js` 或 `package.json` 完整模板 |
| `bt-install` | Shell | 生成 `install.sh` 完整模板 |
| `bt-name` | JS / Python / Shell / HTML | 插入 `{{#plugin_name#}}` 占位符 |
| `bt-title` | JS / Shell | 插入 `{{#plugin_title#}}` 占位符 |

## VSCode 配置说明

项目已配置 `.vscode/settings.json` 和 `.pylintrc`，自动忽略 `{{#plugin_name#}}_main.py` 文件的语法检查。

**开发建议：**
- 使用 `class plugin_name_main:` 作为类名，避免语法检查错误
- 打包时会自动替换为 `class {plugin_name}_main:`
- 文件名 `{{#plugin_name#}}_main.py` 也会自动重命名为 `{plugin_name}_main.py`

**注意事项：**
- 不要手动重命名文件或类名
- 保持 `plugin_name_main` 的命名约定
- 如需调整代码检查规则，可编辑 `.vscode/settings.json` 和 `.pylintrc`

## 许可

MIT License
