
"""
Rayd Hussain

Medical AI/NLP Report Summarizer

7/26/2025 - Present
"""

import sqlite3
import re
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class MedicalReport:
    """Data class to represent a medical report"""
    patient_id: str
    report_date: str
    report_type: str
    diagnosis: str
    symptoms: List[str]
    medications: List[str]
    lab_values: Dict[str, str]
    summary: str
    raw_text: str


class MedicalSummarizer:
    """Lightweight medical report summarizer using only standard library"""

    def __init__(self, db_path: str = "medical_reports.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.setup_database()

        # Medical keywords for extraction
        self.symptoms = [
            'fever', 'headache', 'nausea', 'vomiting', 'diarrhea', 'fatigue',
            'chest pain', 'shortness of breath', 'dizziness', 'cough', 'rash',
            'abdominal pain', 'back pain', 'joint pain', 'muscle pain'
        ]

        self.common_meds = [
            'acetaminophen', 'ibuprofen', 'aspirin', 'lisinopril', 'metformin',
            'atorvastatin', 'amlodipine', 'omeprazole', 'losartan', 'gabapentin'
        ]

    def setup_database(self):
        """Create database schema"""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY,
                patient_id TEXT,
                report_date TEXT,
                report_type TEXT,
                diagnosis TEXT,
                symptoms TEXT,
                medications TEXT,
                lab_values TEXT,
                summary TEXT,
                raw_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    # Note: This function was constructed with the assistance of AI tools
    def extract_patient_info(self, text: str) -> tuple:
        """Extract patient ID and date"""
        # Patient ID patterns
        patient_match = re.search(
            r'(?:patient\s+id|mrn|id)[:\s]+([A-Za-z0-9\-]+)',
            text, re.IGNORECASE)
        patient_id = patient_match.group(1) if patient_match else "UNKNOWN"

        # Date patterns
        date_match = re.search(r'(?:date)[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
                               text, re.IGNORECASE)
        if date_match:
            try:
                date_obj = datetime.strptime(date_match.group(1), '%m/%d/%Y')
                report_date = date_obj.strftime('%Y-%m-%d')
            except:
                report_date = datetime.now().strftime('%Y-%m-%d')
        else:
            report_date = datetime.now().strftime('%Y-%m-%d')

        return patient_id, report_date

    def extract_symptoms(self, text: str) -> List[str]:
        """Find symptoms in text"""
        found_symptoms = []
        text_lower = text.lower()

        for symptom in self.symptoms:
            if symptom in text_lower:
                found_symptoms.append(symptom)

        return found_symptoms

    def extract_medications(self, text: str) -> List[str]:
        """Find medications in text"""
        found_meds = []
        text_lower = text.lower()

        # Look for common medications
        for med in self.common_meds:
            if med in text_lower:
                found_meds.append(med)

        # Look for medication patterns (drug names with dosages)
        med_patterns = re.findall(r'([A-Za-z]+)\s+\d+\s*mg', text,
                                  re.IGNORECASE)
        for med in med_patterns:
            if med.lower() not in found_meds:
                found_meds.append(med.lower())

        return found_meds

    def extract_lab_values(self, text: str) -> Dict[str, str]:
        """Extract lab values"""
        labs = {}

        patterns = {
            'glucose': r'glucose[:\s]+(\d+(?:\.\d+)?)',
            'hemoglobin': r'hemoglobin[:\s]+(\d+(?:\.\d+)?)',
            'cholesterol': r'cholesterol[:\s]+(\d+(?:\.\d+)?)',
            'blood_pressure': r'(?:bp|blood pressure)[:\s]+(\d+/\d+)',
            'temperature': r'temp(?:erature)?[:\s]+(\d+(?:\.\d+)?)'
        }

        for lab_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                labs[lab_name] = match.group(1)

        return labs

    def extract_diagnosis(self, text: str) -> str:
        """Extract diagnosis"""
        patterns = [
            r'diagnosis[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'impression[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'assessment[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                diagnosis = match.group(1).strip()
                return re.sub(r'\s+', ' ', diagnosis)[:200]

        return "No clear diagnosis found"

    def generate_summary(self, report: MedicalReport) -> str:
        """Create a summary"""
        parts = [
            f"Patient: {report.patient_id}",
            f"Date: {report.report_date}",
            f"Type: {report.report_type}"
        ]

        if report.diagnosis != "No clear diagnosis found":
            parts.append(f"Diagnosis: {report.diagnosis}")

        if report.symptoms:
            parts.append(f"Symptoms: {', '.join(report.symptoms[:3])}")

        if report.medications:
            parts.append(f"Medications: {', '.join(report.medications[:3])}")

        if report.lab_values:
            lab_summary = []
            for test, value in list(report.lab_values.items())[:2]:
                lab_summary.append(f"{test}={value}")
            parts.append(f"Labs: {', '.join(lab_summary)}")

        return " | ".join(parts)

    def process_report(self, text: str,
                       report_type: str = "General") -> MedicalReport:
        """Process medical report text"""
        patient_id, report_date = self.extract_patient_info(text)
        symptoms = self.extract_symptoms(text)
        medications = self.extract_medications(text)
        lab_values = self.extract_lab_values(text)
        diagnosis = self.extract_diagnosis(text)

        report = MedicalReport(
            patient_id=patient_id,
            report_date=report_date,
            report_type=report_type,
            diagnosis=diagnosis,
            symptoms=symptoms,
            medications=medications,
            lab_values=lab_values,
            summary="",
            raw_text=text
        )

        report.summary = self.generate_summary(report)
        return report

    def save_report(self, report: MedicalReport) -> int:
        """Save report to database"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO reports 
            (patient_id, report_date, report_type, diagnosis, symptoms, 
             medications, lab_values, summary, raw_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.patient_id,
            report.report_date,
            report.report_type,
            report.diagnosis,
            json.dumps(report.symptoms),
            json.dumps(report.medications),
            json.dumps(report.lab_values),
            report.summary,
            report.raw_text
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_patient_reports(self, patient_id: str) -> List[Dict]:
        """Get all reports for a patient"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM reports WHERE patient_id = ? 
            ORDER BY report_date DESC
        ''', (patient_id,))

        reports = []
        for row in cursor.fetchall():
            report_dict = {
                'id': row[0],
                'patient_id': row[1],
                'report_date': row[2],
                'report_type': row[3],
                'diagnosis': row[4],
                'symptoms': json.loads(row[5]) if row[5] else [],
                'medications': json.loads(row[6]) if row[6] else [],
                'lab_values': json.loads(row[7]) if row[7] else {},
                'summary': row[8]
            }
            reports.append(report_dict)

        return reports

    def search_reports(self, query: str) -> List[Dict]:
        """Search reports by keyword"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, patient_id, report_date, summary 
            FROM reports 
            WHERE raw_text LIKE ? OR diagnosis LIKE ?
            ORDER BY report_date DESC
        ''', (f'%{query}%', f'%{query}%'))

        return [
            {'id': row[0], 'patient_id': row[1], 'date': row[2],
             'summary': row[3]}
            for row in cursor.fetchall()
        ]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM reports')
        total_reports = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT patient_id) FROM reports')
        unique_patients = cursor.fetchone()[0]

        cursor.execute(
            'SELECT report_type, COUNT(*) FROM reports GROUP BY report_type')
        report_types = dict(cursor.fetchall())

        return {
            'total_reports': total_reports,
            'unique_patients': unique_patients,
            'report_types': report_types
        }

    def close(self):
        """Close database connection"""
        self.conn.close()

def load_reports_from_file(filepath: str) -> list[str]:
    """Load multiple reports from a file, separated by ---"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return [r.strip() for r in content.split("---") if r.strip()]


# Example usage
def demo():
    """Demo the summarizer with sample data"""

    # Load reports from file
    reports = load_reports_from_file("reports.txt")

    summarizer = MedicalSummarizer("demo_reports.db")

    try:
        for text in reports:
            report = summarizer.process_report(text, "Imported")
            report_id = summarizer.save_report(report)
            print(f" Report saved with ID: {report_id}")
            print(f"Summary: {report.summary}\n")

        # Show stats
        stats = summarizer.get_stats()
        print(f"Database Stats: {stats}")

    finally:
        summarizer.close()



if __name__ == "__main__":
    demo()
