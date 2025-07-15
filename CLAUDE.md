# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a finance automation project with tools for processing financial documents and bank statements. The project uses Python 3.9.6 and includes:

- **bank-reconciliation/**: Main application directory containing financial data processing tools
- **venv/**: Python virtual environment (note: may need to be recreated as it appears to reference an old path)

## Architecture

The project consists of two main Python applications:

### PDF Processing Application (`app.py`)
- GUI-based PDF to text converter using tkinter
- Extracts text from PDF files using pdfplumber
- Saves extracted text to .txt files for analysis
- Uses pandas for potential Excel export (currently saves as text)

### Bank Statement XML Processor (`convert_file.py`) 
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
pip install pandas pdfplumber tkinter xml
```

## Running Applications

### PDF Converter
```bash
cd bank-reconciliation
python3 app.py
```

### XML Bank Statement Processor
```bash
cd bank-reconciliation
python3 convert_file.py
```

## File Structure

- `app.py`: PDF to text extraction with GUI
- `convert_file.py`: XML bank statement parser
- `output.csv`: Generated CSV output from XML processing
- `CA XML Account statement extended_0220736246_20250715.xml`: Sample bank statement XML file

## Key Dependencies

- `pandas`: Data manipulation and CSV export
- `pdfplumber`: PDF text extraction
- `tkinter`: GUI framework (built into Python)
- `xml.etree.ElementTree`: XML parsing (built into Python)

## Working with Bank Data

The XML processor is designed for ISO 20022 format bank statements. It:
- Handles namespaced XML elements
- Flattens hierarchical transaction data
- Preserves both entry-level and transaction-level details
- Outputs all available fields to CSV for analysis