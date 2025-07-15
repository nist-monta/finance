# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a finance automation project with tools for processing financial documents and bank statements. The project uses Python 3.9.6 and includes:

- **bank-reconciliation/**: Main application directory containing financial data processing tools
- **venv/**: Python virtual environment (note: may need to be recreated as it appears to reference an old path)

## Architecture

The project consists of two main Python applications:

### XML/NDA to CSV Converter (`app.py`)
- GUI-based XML and NDA file converter using tkinter
- Parses ISO 20022 XML bank statements and NDA files
- Extracts comprehensive transaction data including:
  - Account information (IBAN, currency, owner, servicer)
  - Transaction details (amounts, dates, references, descriptions)
  - Related parties (debtor/creditor names, bank information)
  - Statement metadata and balances
- Supports multiple file selection and batch processing
- Outputs processed data to CSV format using pandas
- Includes smart column ordering for better readability

### Bank Statement XML Processor (`convert_file.py`) 
- Command-line version of XML parser
- Parses ISO 20022 XML bank statements
- Flattens XML structure into tabular format
- Extracts transaction details from nested XML entries
- Outputs processed data to CSV format using pandas

## Development Setup

The project uses a Python virtual environment but it appears to need recreation:

```bash
# Create new virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install pandas
```

## Running Applications

### XML/NDA to CSV Converter (GUI)
```bash
cd bank-reconciliation
python3 app.py
```

### XML Bank Statement Processor (Command Line)
```bash
cd bank-reconciliation
python3 convert_file.py
```

## File Structure

- `app.py`: XML/NDA to CSV converter with GUI
- `convert_file.py`: Command-line XML bank statement parser
- `output.csv`: Generated CSV output from XML processing
- `CA XML Account statement extended_0220736246_20250715.xml`: Sample bank statement XML file

## Key Dependencies

- `pandas`: Data manipulation and CSV export
- `tkinter`: GUI framework (built into Python)
- `xml.etree.ElementTree`: XML parsing (built into Python)

## Working with Bank Data

The XML processor is designed for ISO 20022 format bank statements. It:
- Handles namespaced XML elements
- Flattens hierarchical transaction data
- Preserves both entry-level and transaction-level details
- Outputs all available fields to CSV for analysis