# Codefun AutoSubmit

A modern Python package for automating code submissions to Codefun.vn with support for multiple programming languages and a clean, modular architecture.
Based on: https://github.com/Unknown15082/CodefunAutoSubmit

## Features

- 🚀 **Modern Python Package**: Proper package structure with type hints and documentation
- 🌐 **Browser Automation**: Built on Selenium 4 with automatic driver management
- 📝 **Multiple Languages**: Support for C++, Python3, Pascal, and NAsm
- 🎯 **Flexible Submission**: Submit by problem ID or batch submit entire folders
- 📥 **Fetch Submissions**: Download your accepted submissions
- 🛠️ **CLI Interface**: Easy-to-use command-line interface
- ⚙️ **Environment Configuration**: Secure configuration with .env files
- 🔄 **Smart Skipping**: Skip only AC problems or all submitted problems

## Installation

### From Source

```bash
git clone https://github.com/KNN-07/codefun-autosubmit.git
cd codefun-autosubmit
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/KNN-07/codefun-autosubmit.git
cd codefun-autosubmit
pip install -e ".[dev]"
```

## Quick Start

### 1. Setup Configuration

```bash
codefun setup
```

This will guide you through setting up your Codefun credentials and preferences.

### 2. Submit Specific Problems

```bash
# Submit specific problem IDs
codefun auto --tasks 001 002 003

# Or use the package directly
python -m codefun_autosubmit auto --tasks 001 002 003
```

### 3. Batch Submit All Files

```bash
# Submit all files in your configured folder that haven't been accepted yet
codefun batch

# Skip all submitted problems (including non-AC submissions)
codefun batch --skip-submitted
```

### 4. Fetch Accepted Submissions

```bash
# Download all your accepted submissions
codefun fetch
```

## Configuration

The tool uses a `.env` file for configuration. After running `codefun setup`, your `.env` file will look like:

```env
CF_USERNAME=your_username
CF_PASSWORD=your_password
PATH_TO_FOLDER=C:\path\to\your\code\files
LANGUAGE=Python3
CHROME_PATH=chromedriver.exe
```

### Environment Variables

- `CF_USERNAME`: Your Codefun.vn username
- `CF_PASSWORD`: Your Codefun.vn password  
- `PATH_TO_FOLDER`: Absolute path to your code files
- `LANGUAGE`: Default programming language (C++/Python3/Pascal/NAsm)
- `CHROME_PATH`: Path to chromedriver.exe (or "NA" for automatic management)

## Supported Languages

| Language | File Extension | Codefun Value |
|----------|----------------|---------------|
| C++      | `.cpp`         | `C++`         |
| Python3  | `.py`          | `Python3`     |
| Pascal   | `.pas`         | `Pascal`      |
| NAsm     | `.s`           | `NAsm`        |

## Usage Examples

### Programmatic Usage

```python
from codefun_autosubmit import setup_driver, SubmissionManager

# Setup browser driver
driver = setup_driver()
submission_manager = SubmissionManager(driver)

# Submit by problem ID
submission_manager.submit_by_id("001", "Python3")

# Submit a file
submission_manager.submit_file("C:\\path\\to\\P001.py")

# Fetch submissions
accepted = submission_manager.get_all_accepted_submissions()
for sub_id, problem_code in accepted:
    submission_manager.retrieve_submission(sub_id, problem_code, "Python3")

driver.quit()
```

### CLI Commands

```bash
# Show help
codefun --help

# Setup configuration
codefun setup

# Auto submit specific problems
codefun auto --tasks 001 002 003

# Batch submit all pending files (skip only AC problems)
codefun batch

# Batch submit all pending files (skip all submitted problems)
codefun batch --skip-submitted

# Fetch all accepted submissions
codefun fetch
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black codefun_autosubmit/
```

### Type Checking

```bash
mypy codefun_autosubmit/
```

### Linting

```bash
flake8 codefun_autosubmit/
```

## Project Structure

```
codefun_autosubmit/
├── pyproject.toml          # Modern Python packaging
├── setup.py                # Legacy setup script
├── README.md               # This file
├── requirements.txt        # Dependencies
├── codefun_autosubmit/     # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point for python -m
│   ├── cli.py              # Command-line interface
│   ├── core/               # Core functionality
│   │   ├── browser.py      # Browser automation
│   │   ├── submission.py   # Submission logic
│   │   └── utils.py        # Utility functions
│   └── scripts/            # High-level scripts
│       ├── auto_submit.py  # Auto submission
│       ├── batch_submit.py # Batch submission
│       └── fetch_ac.py     # Fetch submissions
└── tests/                  # Test suite
    ├── __init__.py
    └── test_core.py
```

## Requirements

- Python 3.9+
- Google Chrome browser
- Internet connection

## Dependencies

- selenium==4.39.0 - Browser automation
- pyperclip==1.11.0 - Clipboard operations
- python-dotenv==1.2.1 - Environment configuration
- requests==2.32.5 - HTTP requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Disclaimer

Please use this tool in accordance with Codefun's rules and terms of service. The developers strongly discourage any form of plagiarism or academic dishonesty. This tool is intended for educational purposes and legitimate use cases only.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.