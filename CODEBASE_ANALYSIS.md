# perturbopy 代码库分析（2026-04-01）

## 1) 总览

- `perturbopy` 是一个以 **后处理 + 测试框架** 为核心的 Python 包，面向 Perturbo（Fortran 主程序）的结果读取、分析、绘图和回归测试。
- 当前版本在 `pyproject.toml` 与 `setup.py` 中均为 `0.7.2`。
- 代码主体位于 `src/perturbopy/`，按职责拆分为：
  - `postproc/`: 后处理对象模型（calc modes、数据库对象、工具函数）
  - `test_utils/` 与 `testing_code/`: 测试驱动与比较逻辑
  - `generate_input/`: 输入文件生成
  - `io_utils/`: YAML/HDF5 等输入输出工具

## 2) 架构拆解

### 2.1 领域对象层（postproc）

`postproc/calc_modes/` 提供了一组“计算模式对象”（如 `Bands`, `Trans`, `Imsigma`, `DynaRun` 等），并由 `CalcMode` 作为通用基类承载材料基础信息（晶格、倒易晶格、原子位置、介电张量等）。

设计上优点：
- 面向对象封装良好，面向用户 API 比较自然（“从 YAML 构造对象，再调用对象方法分析/绘图”）。
- `postproc/__init__.py` 将常用类汇总导出，使用体验好。

关注点：
- `CalcMode.__init__` 通过 `pop` 读取 `pert_dict['input parameters']['after conversion']` 下字段，**会修改输入字典本体**。若上层调用方期望复用原 dict，可能引入副作用。

### 2.2 数据表示层（dbs）

`RecipPtDB` 抽象了倒易空间点集，统一维护：
- `points_cart` / `points_cryst`
- 当前激活单位 `units` 与 `points`
- 可视化路径 `path`
- 高对称点标签 `labels`

优点：
- 通过 `from_lattice`、`convert_units`、`distances`、`find` 等方法形成完整小闭环，易于复用。

关注点：
- `RecipPtDB.__init__` 与 `from_lattice` 的 `labels={}` 属于可变默认参数，虽然当前实现中有 `copy()`，但仍建议改为 `None` 以避免未来维护时踩坑。

### 2.3 测试层（pytest + 自定义 conftest）

仓库存在两套测试语义：
- `tests/`：偏 Python 包级单元测试（例如常量、晶格工具、calc mode）
- `src/perturbopy/testing_code/`：更接近 Perturbo 工作流/集成测试

`src/perturbopy/conftest.py` 定义了大量 CLI 选项（`--run_qe2pert`、`--config_machine` 等）和动态参数化逻辑，测试驱动能力较强。

关注点：
- 直接 `pytest -q` 时，当前环境若缺失 `config_machine/config_machine.yml` 会在收集阶段抛错，且随后在 `pytest_terminal_summary` 里又可能出现 `no option named 'run_qe2pert'` 的异常链，导致开发者“开箱即测”体验一般。

## 3) 工程化与发布

### 3.1 打包配置

仓库同时维护：
- 现代配置：`pyproject.toml`
- 兼容配置：`setup.py` + `setup.cfg`

现状虽可用，但存在潜在一致性风险（版本号、依赖、入口点需多处同步）。长期建议以 `pyproject.toml` 为单一事实源。

### 3.2 CLI 入口

提供两个脚本入口：
- `input_generation`
- `run-tests`

这能覆盖常见用户流程，但建议在 README 中补充更具体参数示例（尤其是 `run-tests` 与 `config_machine.yml` 的关系）。

## 4) 当前可见风险与改进优先级

### P0（高优先）
1. **测试可运行性改进**：
   - 在 README 或测试文档中显式给出最小可运行命令（例如只跑 `tests/`，跳过 qe2pert 依赖路径）。
   - 对 `config_machine.yml` 缺失场景改成更友好的 skip 或提前提示。

2. **pytest 选项健壮性**：
   - `pytest_terminal_summary` 中调用 `getoption('run_qe2pert')` 前增加兜底（如先检查 option 是否存在），避免异常链污染输出。

### P1（中优先）
3. **避免副作用**：
   - `CalcMode.__init__` 避免对入参 dict 做 `pop`（改为 `get` + 明确复制）。

4. **可变默认参数整改**：
   - `labels={}` -> `labels=None`，函数内再标准化。

### P2（可选优化）
5. **打包配置收敛**：
   - 减少 `setup.py` / `setup.cfg` 与 `pyproject.toml` 的重复定义。

6. **代码质量基线**：
   - 增加 `ruff` / `black` / `mypy`（或最小子集）到 CI，降低长期维护成本。

## 5) 适合后续演进的方向

- 逐步把“集成测试能力（依赖外部程序/数据）”与“纯 Python 单测”在目录与命令层面彻底区分，给出明确命令别名。
- 为 `postproc` 建立更统一的抽象协议（例如每个 calc mode 的公共属性、单位转换接口、绘图接口约定）。
- 为关键对象（如 `RecipPtDB`, `CalcMode`）补充类型注解，方便 IDE 与静态分析。

---

如果你愿意，我下一步可以直接给出一份“低风险改动 PR 清单”（例如先做测试健壮性 + 文档补强，不改核心数值逻辑）。
