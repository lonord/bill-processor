# Bill Processor

A comprehensive data processing module that filters and standardizes transaction records from multiple payment platforms, storing them in a unified format within a SQLite database.

[中文文档 / Chinese Documentation](README_zh.md)

## Features

- **Multi-format Support**: Process bills from Alipay (CSV), WeChat Pay (Excel), and China Merchants Bank Credit Card (CSV)
- **Automatic File Detection**: Intelligently identifies file types and selects appropriate processors
- **Unified Data Storage**: Standardizes all transaction data into a consistent SQLite database format
- **Command-line Interface**: Easy-to-use CLI with customizable parameters
- **Error Handling**: Robust error handling with detailed logging
- **Incremental Processing**: Only processes files modified since last run
- **Extensible Architecture**: Easy to add new payment platform processors

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lonord/bill-processor.git
cd bill-processor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize Database

First-time setup requires database creation:

```bash
python setup_database.py
```

### 2. Process Bill Files

Basic usage (with default parameters):
```bash
python main.py
```

Custom parameters:
```bash
python main.py --bill-dir /path/to/bills --db-path /path/to/database.sqlite
```

### 3. View Help

```bash
python main.py --help
```

### 4. List Available Processors

```bash
python main.py --list-processors
```

## Command Line Options

- `--bill-dir, -d`: Bill file directory path (default: extract)
- `--db-path, -db`: Database file path (default: billing.sqlite)
- `--list-processors, -l`: List all available processors

## Supported File Formats

### Alipay Bills
- **File Pattern**: `alipay_*.csv`
- **Encoding**: UTF-8/GBK/GB2312 (auto-detected)
- **Source**: Alipay transaction details export

### WeChat Pay Bills
- **File Pattern**: `wechat_*.xlsx`
- **Format**: Excel files
- **Source**: WeChat Pay transaction history export

### China Merchants Bank Credit Card Bills
- **File Pattern**: `cmbcc_*.csv`
- **Encoding**: UTF-8
- **Source**: CMB credit card transaction export

## Database Schema

The `BILL` table contains the following fields:

| Field Name | Type | Description |
|------------|------|-------------|
| ID | TEXT | Primary key, unique bill identifier |
| TIME | TEXT | Transaction time (yyyy-MM-dd HH:mm format) |
| AMOUNT | DECIMAL(10,2) | Transaction amount (max 2 decimal places) |
| CURRENCY | TEXT | Currency type |
| TYPE | TEXT | Transaction type |
| INFO | TEXT | Transaction information |
| NOTE | TEXT | Additional notes |
| SOURCE | TEXT | Bill source platform |
| UPDATE_TIME | INTEGER | Record update time (Unix timestamp) |

## Project Structure

```
bill-processor/
├── main.py                 # Main entry point
├── setup_database.py       # Database initialization script
├── requirements.txt        # Python dependencies
├── billing.sqlite         # SQLite database file
├── processors/            # Processor modules directory
│   ├── __init__.py        # Module initialization
│   ├── base_processor.py  # Base processor class
│   ├── alipay_processor.py # Alipay processor
│   ├── wechat_processor.py # WeChat Pay processor
│   ├── cmbcc_processor.py  # CMB credit card processor
│   └── simple_processor.py # Simple CSV processor
└── extract/               # Bill files directory
    ├── alipay_*.csv
    ├── wechat_*.xlsx
    └── cmbcc_*.csv
```

## Example Output

```
Bill Processor
============================================================
Bill directory: C:\Users\lonord\dev\projects\bill-processor\extract
Database file: C:\Users\lonord\dev\projects\bill-processor\billing.sqlite
============================================================
Loaded 3 processors
Found 3 files in directory extract

Processing file: alipay_支付宝交易明细(20250701-20250731).csv
  Using processor: AlipayProcessor
  Started processing file: extract\alipay_支付宝交易明细(20250701-20250731).csv
  Parsed 134 records from file
  Successfully saved 134 records to database
  ✓ Successfully processed, saved 134 records

Processing completed!
Successfully processed files: 2
Total records: 178

✓ Successfully processed 2 files
```

## Extending Processors

### Adding New Processors

1. Create a new processor file in the `processors/` directory
2. Inherit from `BaseProcessor` class and implement required methods
3. Register the new processor in `processors/__init__.py`

Example:

```python
# processors/new_processor.py
from .base_processor import BaseProcessor, BillRecord

class NewProcessor(BaseProcessor):
    def can_process(self, file_path: str) -> bool:
        # Implement file matching logic
        return file_path.endswith('.new_format')
    
    def process_file(self, file_path: str) -> List[BillRecord]:
        # Implement file processing logic
        records = []
        # ... processing logic ...
        return records
```

```python
# processors/__init__.py
from .new_processor import NewProcessor

# Add to AVAILABLE_PROCESSORS list
AVAILABLE_PROCESSORS = [
    AlipayProcessor,
    WechatProcessor,
    CmbccProcessor,
    SimpleProcessor,
    NewProcessor  # New addition
]
```

## Troubleshooting

### Common Issues

1. **Encoding Errors**: The program automatically tries multiple encoding formats
2. **Excel File Reading Issues**: Ensure pandas and openpyxl libraries are installed
3. **Database Not Found**: Run `python setup_database.py` to create the database first
4. **File Format Mismatch**: Check that filenames follow the required naming patterns

### Debug Mode

For detailed error information, the program outputs specific error causes and locations when issues occur.

## Important Notes

1. Ensure bill files are placed in the correct directory
2. Filenames must follow the specified naming conventions
3. WeChat Pay Excel files require pandas and openpyxl libraries
4. The program automatically handles encoding issues by trying different formats
5. Re-running the program won't create duplicate records (based on ID deduplication)
6. When adding new processors, remember to update the `processors/__init__.py` file

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.