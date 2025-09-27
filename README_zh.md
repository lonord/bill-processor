# 账单处理器

一个综合的数据处理模块，用于过滤和标准化来自多个支付平台的交易记录，并将它们以统一格式存储到SQLite数据库中。

[English Documentation](README.md)

## 功能特性

- **多格式支持**：处理支付宝（CSV）、微信支付（Excel）和招商银行信用卡（CSV）账单
- **自动文件识别**：智能识别文件类型并选择合适的处理器
- **统一数据存储**：将所有交易数据标准化为一致的SQLite数据库格式
- **命令行界面**：易于使用的CLI，支持自定义参数
- **错误处理**：强大的错误处理和详细日志记录
- **增量处理**：只处理自上次运行以来修改的文件
- **可扩展架构**：轻松添加新的支付平台处理器

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/lonord/bill-processor.git
cd bill-processor
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 初始化数据库

首次使用需要创建数据库：

```bash
python setup_database.py
```

### 2. 处理账单文件

基本用法（使用默认参数）：
```bash
python main.py
```

自定义参数：
```bash
python main.py --bill-dir /path/to/bills --db-path /path/to/database.sqlite
```

### 3. 查看帮助

```bash
python main.py --help
```

### 4. 列出可用处理器

```bash
python main.py --list-processors
```

## 命令行选项

- `--bill-dir, -d`：账单文件目录路径（默认：extract）
- `--db-path, -db`：数据库文件路径（默认：billing.sqlite）
- `--list-processors, -l`：列出所有可用的处理器

## 支持的文件格式

### 支付宝账单
- **文件模式**：`alipay_*.csv`
- **编码**：UTF-8/GBK/GB2312（自动检测）
- **来源**：支付宝交易明细导出

### 微信支付账单
- **文件模式**：`wechat_*.xlsx`
- **格式**：Excel文件
- **来源**：微信支付账单流水导出

### 招商银行信用卡账单
- **文件模式**：`cmbcc_*.csv`
- **编码**：UTF-8
- **来源**：招商银行信用卡交易导出

## 数据库结构

`BILL` 表包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| ID | TEXT | 主键，账单唯一标识 |
| TIME | TEXT | 交易时间（yyyy-MM-dd HH:mm格式） |
| AMOUNT | DECIMAL(10,2) | 交易金额（最多2位小数） |
| CURRENCY | TEXT | 货币类型 |
| TYPE | TEXT | 交易类型 |
| INFO | TEXT | 交易信息 |
| NOTE | TEXT | 备注 |
| SOURCE | TEXT | 账单来源平台 |
| UPDATE_TIME | INTEGER | 记录更新时间（Unix时间戳） |

## 项目结构

```
bill-processor/
├── main.py                 # 主入口文件
├── setup_database.py       # 数据库初始化脚本
├── requirements.txt        # Python依赖包
├── billing.sqlite         # SQLite数据库文件
├── processors/            # 处理器模块目录
│   ├── __init__.py        # 模块初始化文件
│   ├── base_processor.py  # 基础处理器类
│   ├── alipay_processor.py # 支付宝处理器
│   ├── wechat_processor.py # 微信支付处理器
│   ├── cmbcc_processor.py  # 招商银行信用卡处理器
│   └── simple_processor.py # 简单CSV处理器
└── extract/               # 账单文件目录
    ├── alipay_*.csv
    ├── wechat_*.xlsx
    └── cmbcc_*.csv
```

## 示例输出

```
账单处理器
============================================================
账单目录: C:\Users\lonord\dev\projects\bill-processor\extract
数据库文件: C:\Users\lonord\dev\projects\bill-processor\billing.sqlite
============================================================
加载了 3 个处理器
在目录 extract 中找到 3 个文件

处理文件: alipay_支付宝交易明细(20250701-20250731).csv
  使用处理器: AlipayProcessor
  开始处理文件: extract\alipay_支付宝交易明细(20250701-20250731).csv
  从文件中解析出 134 条记录
  成功保存 134 条记录到数据库
  ✓ 成功处理，保存了 134 条记录

处理完成!
成功处理文件数: 2
总记录数: 178

✓ 成功处理了 2 个文件
```

## 扩展处理器

### 添加新的处理器

1. 在 `processors/` 目录下创建新的处理器文件
2. 继承 `BaseProcessor` 类并实现必要的方法
3. 在 `processors/__init__.py` 中注册新的处理器

示例：

```python
# processors/new_processor.py
from .base_processor import BaseProcessor, BillRecord

class NewProcessor(BaseProcessor):
    def can_process(self, file_path: str) -> bool:
        # 实现文件匹配逻辑
        return file_path.endswith('.new_format')
    
    def process_file(self, file_path: str) -> List[BillRecord]:
        # 实现文件处理逻辑
        records = []
        # ... 处理逻辑 ...
        return records
```

```python
# processors/__init__.py
from .new_processor import NewProcessor

# 添加到 AVAILABLE_PROCESSORS 列表
AVAILABLE_PROCESSORS = [
    AlipayProcessor,
    WechatProcessor,
    CmbccProcessor,
    SimpleProcessor,
    NewProcessor  # 新增
]
```

## 故障排除

### 常见问题

1. **编码错误**：程序会自动尝试多种编码格式
2. **Excel文件读取问题**：确保安装了pandas和openpyxl库
3. **数据库不存在**：先运行`python setup_database.py`创建数据库
4. **文件格式不匹配**：检查文件名是否符合命名规则

### 调试模式

如果遇到问题，程序会输出具体的错误原因和位置，便于调试。

## 重要注意事项

1. 确保账单文件放在正确的目录中
2. 文件名必须符合指定的命名规则
3. 微信支付Excel文件需要安装pandas和openpyxl库
4. 程序会自动处理编码问题，尝试不同格式
5. 重复运行程序不会产生重复记录（基于ID去重）
6. 新增处理器时记得更新 `processors/__init__.py` 文件

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行修改
4. 如适用，添加测试
5. 提交拉取请求

## 支持

如有问题和疑问，请在GitHub仓库中提交issue。
