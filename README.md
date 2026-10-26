# NextAgent / SkillsBench 独立评测项目

用普通终端即可运行，不需要 Codex、Claude、ChatGPT 或宿主机 Node.js。统一入口是 `python bench.py`，Windows 也可继续使用项目中的 PowerShell 脚本。

## 环境

- Python 3.12+，推荐3.12，包含 venv/pip。
- 可用的 Linux amd64 Docker 服务；完整题库需要 Docker Compose v2。
- 自己的 NextAgent Linux x64 编译包和可用模型API key。本项目的`datasets/`已包含固定的87题，随项目文件夹保留即可。
- 能访问镜像仓库、软件源、任务依赖下载站点和模型服务。
- 足够的Docker内存与磁盘。16 GiB题目至少需要Docker可见20 GiB内存；任务资源不因并发而降低。

完整说明、系统差异、凭据与移交要求见 [环境准备文档](docs/ENVIRONMENT.md)。

## 第一次使用

直接进入项目文件夹，本机为`C:\Project\nextagent-bench`；不需要解压或使用`dist/`中的ZIP。Linux/macOS 若使用 python3，将以下 python 替换为 python3：

```text
python bench.py setup --framework /path/to/nextagent-linux-x64.tar.gz
```

首次安装只需上述框架参数。这会创建本项目虚拟环境、安装依赖、运行本地测试并导入输入。仅当项目中未携带题库或更换题库时，追加`--dataset /path/to/skillsbench`。支持原始框架包、部署目录或外部已导入的冻结输入目录，不要求别人具有原机器的文件路径。没有宿主机tar时优先提供tar.gz。

题库随项目放在`datasets/<sha>/`，路径适配代码及`profiles/path-mappings.yaml`也随包交付。每题运行时自动生成适合NextAgent工作区的任务/Skill文本和路径桥接；原始题目、verifier/oracle保持原样，不需要使用者逐题改路径，也不要把某个旧attempt的工作区作为题库复制。

在自己的终端设置 `OPENAI_API_KEY`，或复制 `credentials.example.json` 为不提交Git的 `credentials.local.json`，填写自己的key。Windows的加密凭据不能复制给另一个用户。

```text
python bench.py doctor
python bench.py run --suite smoke --jobs 2 --credentials-file credentials.local.json
python bench.py run --suite full --jobs 2 --credentials-file credentials.local.json --background
```

若已设置环境变量，不需要 `--credentials-file`。环境检查不调用模型；smoke和full会实际调用模型并消耗账号配额。多个共享账号key不能叠加额度。

## 后续换框架与管理

```text
python bench.py run --framework /path/to/new-release.tar.gz --suite full --jobs 2 --background
python bench.py status
python bench.py metrics <run-id>
python bench.py concurrency <run-id> --jobs 3 --reason 'Operator requested'
python bench.py stop <run-id>
python bench.py resume <run-id> --background
python bench.py report <run-id>
```

更换新包建立新批次，不覆盖旧结果。默认恢复只补未完成/中断任务，已结束任务不自动重跑。后台进程由Python启动，stdout、stderr和PID在launches；不依赖Codex或任何聊天保持在线。

## 配置和产物

- `evaluation.yaml`：默认输入、模型/服务地址、并发和任务集。
- `profiles/default-system.yaml`：框架系统配置；`profiles/agent.yaml`：Agent配置。新包不会覆盖这两份模板。
- `profiles/model-quota.yaml`：共享模型额度；`profiles/path-mappings.yaml`：任务路径映射；`profiles/analysis.yaml`：失败分析开关和预算。
- 开发诊断插件/Hook完全按两份框架配置声明使用，不删除、补写或强制启用，也不增加Hook启动校验。轨迹由框架生成，评测器原样归档。

每次输出 `RUN_DIRECTORY`。`runs/<run-id>/results.xlsx`、`report.md`、`results.json`为汇总，`tasks/<task>/attempt-*/result.json`是逐题入口。原生日志在`nextagent-home/logs`，完整workspace和日志在`nextagent-home.tar`，模型交换证据在`model-gateway/*/exchanges.tar`。保留每次attempt，以首次有效分数为主，不通过重跑覆盖原失败。

原始数据包含任务内容和工作区，应按本地评测证据保存。源码移交不包含这些原文。失败分析不能把证据不足的假设写成确定根因；纯环境失败与模型答错分开统计。

## 给别人使用

直接复制`nextagent-bench`项目文件夹即可，保留代码、配置、`datasets/`、说明和测试。`dist/`是可选压缩包产物，不参与安装、启动或评测，无需一起复制。

移交时跳过以下本机文件；本机原文件和历史结果继续保留：

- `.secrets/`、`credentials.local.json`、`.env*`：本人的凭据，对方应配置自己的key。
- `.venv/`、`*.egg-info/`、`__pycache__/`：对方首次执行setup会重新安装。
- `.git/`、`.state/`、`cache/`、`launches/`、`prepared.json`、`dist/`：版本历史、本机运行状态或可重新生成的数据。
- `artifacts/`：已导入的旧框架可省略，对方指定自己的新框架压缩包。
- `runs/`：历史结果不是启动依赖；需要共享结果时，单独提供相应批次。

对方进入复制后的项目文件夹，执行本说明的首次安装命令并设置自己的凭据，即可评测；不需要原机器的目录或Codex。

只有需要压缩传输时才使用以下可选命令：

```text
python bench.py bundle --with-dataset --output dist/nextagent-bench-ready.zip
```

生成代码及已固定题库的ZIP，排除凭据、虚拟环境、历史结果、运行缓存和框架二进制；会核对题库文件摘要，保留题库许可。接收者解压后按首次安装步骤启动。省略`--with-dataset`仍可生成不含题库的纯源码包，接收者需另指定题库。完整移交清单见 [环境文档](docs/ENVIRONMENT.md#移交源码)。
