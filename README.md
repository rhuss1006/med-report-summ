# Medical AI/NLP Report Summarizer

A lightweight Python application for processing, extracting, and summarizing medical reports using only library components.

## Overview

This project demonstrates automated medical information extraction from unstructured text reports. The system processes raw medical reports and transforms them into structured data stored in SQLite, enabling quick searches and patient history tracking.

## Files

* `sample.py` - Main application with complete functionality
  * Medical report processing and information extraction
  * SQLite database management
  * Patient history tracking
  * Search and statistics functionality
  * Batch processing from text files

* `reports.txt` - Sample medical reports dataset
  * 5 sample reports covering different medical scenarios
  * Primary care visits, ER reports, inpatient notes
  * Demonstrates various report formats and medical conditions

## Features

* **Automated Information Extraction**: Extracts patient IDs, dates, symptoms, medications, lab values, and diagnoses
* **Database Storage**: Stores processed reports in SQLite for easy retrieval
* **Report Summarization**: Generates concise summaries highlighting key medical information
* **Patient History**: Track all reports for individual patients chronologically
* **Search Functionality**: Find reports by keywords or medical terms
* **Statistics Dashboard**: View database statistics and report type breakdowns
* **Batch Processing**: Process multiple reports from text files

## Requirements

```
# No external dependencies - uses Python standard library only
sqlite3
re
json
datetime
dataclasses
typing
```

## Usage

Run the demo to process sample reports:

```bash
python sample.py
```

Process your own medical reports:

```python
from sample import MedicalSummarizer

# Initialize the summarizer
summarizer = MedicalSummarizer("my_reports.db")

# Process a single report
report = summarizer.process_report(report_text, "Primary Care")
report_id = summarizer.save_report(report)

# Get patient history
patient_reports = summarizer.get_patient_reports("P-001")

# Search reports
results = summarizer.search_reports("chest pain")

# View statistics
stats = summarizer.get_stats()

summarizer.close()
```

## Data Structure

**MedicalReport Class**
* `patient_id` - Patient identifier
* `report_date` - Report date (YYYY-MM-DD format)
* `report_type` - Type of medical report
* `diagnosis` - Primary diagnosis extracted
* `symptoms` - List of identified symptoms
* `medications` - List of current medications
* `lab_values` - Dictionary of laboratory test results
* `summary` - Generated one-line summary
* `raw_text` - Original report text

## Extraction Capabilities

**Automatically Detects:**
* Patient information (IDs, dates)
* Common symptoms (fever, headache, chest pain, nausea, etc.)
* Medications (common drugs and dosage patterns)
* Lab values (glucose, hemoglobin, blood pressure, temperature)
* Diagnoses from assessment sections

**Supported Report Types:**
* Primary Care Visits
* Emergency Room Reports
* Inpatient Progress Notes
* Outpatient Clinic Notes
* Follow-up Visits

## Sample Output

```
Report saved with ID: 1
Summary: Patient: P-001 | Date: 2024-03-20 | Type: Primary Care | Diagnosis: Essential hypertension, well controlled | Symptoms: fatigue, headache | Medications: lisinopril, metformin

Database Stats: {'total_reports': 5, 'unique_patients': 5, 'report_types': {'Imported': 5}}
```

## Limitations

* Uses basic pattern matching and keyword detection
* Limited to predefined medical terms and patterns
* No advanced NLP or machine learning capabilities
* Requires consistent report formatting for optimal extraction
* Designed for structured medical report formats

**Author**

Rayd Hussain - 7/26/2025 - Present
