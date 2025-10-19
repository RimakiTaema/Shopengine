# Shop Converter - Executable Versions

This directory contains multiple ways to run the Shop Converter:

## 1. Standalone Executable (Recommended)
- **File**: `dist/shop-converter`
- **Usage**: `./dist/shop-converter [init]`
- **Description**: Self-contained executable that includes all dependencies

### Examples:
```bash
# Initialize folder structure
./dist/shop-converter init

# Run the converter
./dist/shop-converter
```

## 2. Python Script with Launcher
- **File**: `shop-converter.py` + `run-shop-converter.sh`
- **Usage**: `./run-shop-converter.sh [init]`
- **Description**: Python script with a launcher that sets up the environment

### Examples:
```bash
# Initialize folder structure
./run-shop-converter.sh init

# Run the converter
./run-shop-converter.sh
```

## 3. Direct Python Script (if PYTHONPATH is set)
- **File**: `shop-converter.py`
- **Usage**: `PYTHONPATH=/workspace python3 shop-converter.py [init]`
- **Description**: Direct execution with manual PYTHONPATH setup

### Examples:
```bash
# Initialize folder structure
PYTHONPATH=/workspace python3 shop-converter.py init

# Run the converter
PYTHONPATH=/workspace python3 shop-converter.py
```

## Features Fixed
- ✅ Fixed `ModuleNotFoundError: No module named 'converter.constants'`
- ✅ Added fallback console mode when terminal UI is not available
- ✅ Created standalone executable using PyInstaller
- ✅ Added launcher script for easy execution
- ✅ Fixed console mode to work properly without curses
- ✅ Added proper error handling and user feedback in console mode

## Notes
- The executable is built for Linux x86_64 systems
- All versions will fall back to console mode if the terminal doesn't support curses
- The converter will create a `shops_to_convert` directory structure when you run `init`
- Place your shop configuration files in the appropriate plugin subdirectories
- Console mode provides clear feedback and progress information
- The converter supports interactive price configuration in console mode

## Tested Working Features
- ✅ Console mode conversion (no curses required)
- ✅ Interactive price configuration
- ✅ Shop data collection and processing
- ✅ Output file generation
- ✅ Error handling and user feedback
- ✅ Both Python script and executable versions