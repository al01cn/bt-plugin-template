# 宝塔面板插件 DEMO

一个最小化的宝塔 Linux 面板第三方插件模板，用于快速开始插件开发。

## 项目结构

```
demo/
├── package.json                    # 插件信息（统一管理，修改这里即可）
├── src/                            # 源码目录（也是插件的实际目录结构）
│   ├── info.json                   # 由 pack.py 自动生成，不入 git
│   ├── install.sh                  # 由 pack.py 从 .tpl 自动生成，不入 git
│   ├── icon.png                    # 插件图标（建议 96x96 PNG）
│   ├── index.html                  # 前端面板页面（宝塔内嵌渲染）
│   ├── demo_main.py                # 后端主程序（运行时从 info.json 读取信息）
│   ├── templates/
│   │   └── index.html              # Jinja2 模板页面（保留原生 {{ }} 语法）
│   └── static/
│       └── js/
│           ├── package.js.tpl      # 前端信息模板（入库跟踪）
│           ├── package.js          # 由 pack.py 从 .tpl 自动生成，不入 git
│           └── main.js             # 前端交互脚本（从 window.__BT_PLUGIN__ 读取信息）
├── dist/                           # 打包输出（自动生成，不要手动修改）
├── pack.py                         # 打包脚本
├── .gitignore
└── README.md
```

## 设计思路

**核心原则：源码文件零占位符，不影响代码审查。**

- `main.js`、`index.html`、`demo_main.py` 等源码文件中**没有任何占位符**，直接写死 `demo` 或通过运行时读取
- 插件信息集中在根目录 `package.json` 管理，打包时自动生成以下文件：
  - `src/info.json` — 宝塔插件配置
  - `src/install.sh` — 安装/卸载脚本（从 `install.sh.tpl` 生成）
  - `src/static/js/package.js` — 前端信息对象（从 `package.js.tpl` 生成）
- `.tpl` 模板文件入库跟踪，生成的实际文件通过 `.gitignore` 排除
- 占位符语法 `{{#字段名#}}` **仅存在于 `.tpl` 文件中**

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

### 2. 重命名主程序文件

将 `src/demo_main.py` 重命名为 `{name}_main.py`，类名也要对应修改。运行时会从同目录 `info.json` 读取版本号等信息。

### 3. 开发后端 API

在 `_main.py` 中添加方法即可暴露为 API：

```python
class your_plugin_main:
    def your_method(self, args):
        # args 是前端传来的参数字典
        return {"key": "value"}  # 自动序列化为 JSON
```

### 4. 打包

```bash
# 默认打包（版本号读取 package.json）
python pack.py

# 指定版本号（仅影响本次打包，不修改 package.json）
python pack.py --version 1.1
```

打包流程：
1. 读取 `package.json`
2. 从 `.tpl` 模板生成 `install.sh`、`package.js`（替换 `{{#字段名#}}` 占位符）
3. 生成 `info.json`
4. 打包 `src/` 为 zip（排除 `.tpl` 文件）

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

## 许可

MIT License
