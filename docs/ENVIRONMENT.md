# 独立部署环境与操作说明

项目通过普通终端执行 Python 和 Docker。不需要安装 Codex、Claude、ChatGPT、宿主机 Node.js 或 Excel，不依赖它们的登录态、目录、工具或定时任务。`bench.py` 是通用入口，PowerShell 脚本是可选的 Windows 便捷入口。

## 必须准备

| 项目 | 要求 |
|---|---|
| 系统 | Windows、Linux 或 macOS；Docker 使用 Linux amd64 容器。推荐 x86_64 主机。ARM 主机本地运行本包未验证，可连接 amd64 Docker 服务；不能直接换成 ARM 框架后混算成绩。 |
| Python | Python 3.12 或更新，推荐已验证的3.12；需要 venv、ensurepip/pip。某些 Linux 发行版需另外安装 python3-venv。 |
| Docker | Docker Desktop 或 Docker Engine，当前用户能执行 docker info。完整题库需要 Compose v2：docker compose version。 |
| 网络 | Python包源、Docker镜像仓库、模型API，以及任务使用的 Ubuntu/Debian、npm、PyPI、GitHub、Hugging Face 等下载源。不能通过关闭TLS或软件源验签规避错误。 |
| 模型 | 框架支持的 OpenAI-compatible 模型接口、自己的API key、可用余额和模型授权。模型与地址在 evaluation.yaml 设置。 |
| 框架 | 完整 Linux x64 编译包 tar.gz，含 candidate-manifest.json、@nextagent/agent-app 及配置声明的开发诊断插件。也支持已解压部署目录；目录导入另外需要宿主机 tar 命令。 |
| 题库 | 当前项目文件夹已包含固定的87题，保留datasets/<sha>/即可，无需额外参数。未携带题库或换题库时提供SkillsBench根目录，包含 tasks/<task>/task.md、environment、verifier；也支持外部冻结目录。 |
| 权限/空间 | 项目可写，Docker和项目磁盘有空间保存所选题的镜像、依赖、workspace和轨迹。首次构建没有缓存，可能较慢。 |

项目不会自动安装Docker、调整系统代理/WSL内存或重启服务。Linux的Docker socket权限应由机器管理员配置，不要求以root运行整个评测器。

## 内存和并发

调度使用Docker实际可见总内存的80%，每题按sandbox.memory_mb预约。16 GiB题目要求Docker可见总内存至少20 GiB；本机WSL2上限22 GiB实际得到21.5 GiB可见内存、17.2 GiB调度预算。这只是验证示例，不能在其他机器上未经确认照改全局设置。

从2并发开始即可。增加并发不能解决单题内存不足。共享账号的多个key不能叠加额度；总并发、RPM/TPM和等待上限在profiles/model-quota.yaml设置。本地互斥锁只约束本项目，跨机器共享账号时仍需协调总配额。

## 首次安装

直接进入项目文件夹即可；本机为C:\Project\nextagent-bench。复制项目文件夹给别人也不需要使用dist或ZIP。只有通过压缩包移交时才需要先解压。Linux/macOS如果命令名是python3，以下python均替换为python3。

```text
python --version
docker info
docker compose version
python bench.py setup --framework /path/to/nextagent-linux-x64.tar.gz
```

Windows也可直接用Python入口，不需要更改PowerShell执行策略；或者使用便捷脚本：

```powershell
.\Setup.ps1 -Framework 'D:\inputs\nextagent-linux-x64.tar.gz'
```

上述命令适用于保留datasets/的项目文件夹。未携带题库或换题库时追加`--dataset /path/to/skillsbench`（PowerShell脚本用`-Dataset`）。Setup创建本项目的.venv，按pyproject.toml安装依赖，运行不调用模型的本地测试，再导入输入并将evaluation.yaml默认输入改为项目相对路径。可用`--skip-tests`跳过安装测试，`--skip-import`只安装代码。不要从别人机器复制.venv，目标机器应重新安装。本机环境安装完成后，换框架直接执行run --framework即可，不必每次重新setup。

路径适配由评测器自动完成，不要求使用者修改题库。代码根据镜像实际WORKDIR和profiles/path-mappings.yaml，将Agent看到的任务/Skill路径映射到workspace/temp，并在容器内桥接原路径。题库文件及评分器/oracle保持原样；每次attempt保留agent-facing/adaptation.json和adaptation.patch作为审计。不能把旧运行目录中的agent-facing产物当成新的题库。

Windows建议选择较短的项目目录。程序的本地Python文件操作支持深层Skill文件的扩展路径，不需要为了题库复制去修改系统长路径策略；外部Docker/tar工具仍受其自身路径能力限制。

## 设置自己的凭据

单key使用环境变量，不把key作为启动参数：

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = '<your-own-key>'
python bench.py doctor
```

```sh
# Linux / macOS
export OPENAI_API_KEY='<your-own-key>'
python3 bench.py doctor
```

多key可复制credentials.example.json为credentials.local.json，填写自己的name/key列表：

```text
python bench.py run --suite full --jobs 2 --credentials-file credentials.local.json --background
```

该文件是明文，应限制本机访问，不发给别人，不提交Git。也支持NAB_API_KEYS JSON环境变量。Windows的Set-ModelCredential.ps1仍可保存当前用户的DPAPI加密凭据，通用入口可读取；加密文件绑定用户/机器，不能给另一个人复用。只有未提供环境凭据时才读取本机加密凭据。

doctor不调用模型，不检查余额；模型开通/余额由使用者确认。CLI、启动记录和结果不打印key。

## 启动与管理

```text
python bench.py run --suite full --jobs 2 --background
python bench.py status
python bench.py metrics <run-id>
python bench.py concurrency <run-id> --jobs 3 --reason 'Operator requested'
python bench.py stop <run-id>
python bench.py resume <run-id> --background
python bench.py report <run-id>
```

`--credentials-file`可用于run/resume/analyze/doctor等命令。`--background`启动独立进程，在launches中记录PID、stdout和stderr。不安装或关闭Codex不会影响运行。默认恢复跳过已结束任务，额外重跑需要明确指定，不会自动反复跑到成功。

更换框架：`python bench.py run --framework /path/to/new-release.tar.gz --suite full --jobs 2 --background`。两份profiles配置保留，不从新包覆盖。开发诊断插件和Hook直接按配置使用，框架生成轨迹，评测器原样归档，不增加Hook启动校验。

每次输出RUN_DIRECTORY。runs/<run-id>下的results.xlsx、report.md、results.json是汇总；每题产物在tasks目录。原生日志在nextagent-home/logs，完整工作区和日志在nextagent-home.tar。失败分析可能在manifest显示FINISHED后继续，runner.lock消失、进程退出后才是全部收尾。源码变化后的冻结检查仍生效，不能改旧摘要绕过。

## 移交源码

默认直接复制项目文件夹，保留bench.py、pyproject.toml、evaluation.yaml、profiles/、nextagent_bench/、scripts/、tests/、docs/、datasets/及说明和便捷脚本。题库路径是项目相对路径，对方只需指定自己的框架包，不依赖原机器的位置。

复制时排除.secrets/、credentials.local.json和.env*；对方使用自己的凭据。也排除.venv/、*.egg-info/、__pycache__/、.git/、.state/、cache/、launches/、prepared.json、dist/。artifacts/中的旧框架无需随项目移交，setup会导入对方指定的压缩包。runs/不属于启动依赖，若要共享历史结果，单独提供需要的批次。这里只规定复制范围，不删除原机器的凭据或历史结果。

dist只存放可选压缩包，不参与安装、运行或结果读取。需要压缩传输时才使用：

```text
python bench.py bundle --with-dataset --output dist/nextagent-bench-ready.zip
```

可选压缩包包含代码、配置模板、测试、本文档和当前固定的87题（含原有LICENSE）。打包时核对题库摘要，只复制冻结清单内的任务文件；evaluation.yaml保留项目相对题库路径。接收者解压后提供新的框架压缩包和自己的凭据，无需准备原机器的题库路径。

不加`--with-dataset`时生成纯源码包nextagent-bench-portable.zip，题库路径重置为inputs/skillsbench占位路径；这种包才需要接收者额外提供题库。两种包均不含API key、加密凭据、虚拟环境、Codex配置、历史结果或框架二进制。模型、配额及两份框架配置仍沿用模板。

题库已内置时无需另外复制。纯源码包需要相同输入时，可另外移交artifacts/<sha>、datasets/<sha>冻结输入目录，接收人将其作为setup参数。不要将.secrets、.venv或含业务原文的runs目录作为源码发出。镜像缓存不随项目分发，目标机器首次运行会正常重建。

缺外部数据、GPU、下载源不可达、模型未开通或内存不足时会留下相应错误。项目不能保证任意题库在任意硬件上一次通过，环境失败也不能当作模型答错。
