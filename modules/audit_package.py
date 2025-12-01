"""
Audit Package Exporter
Creates comprehensive ZIP package with all validation artifacts
"""

import os
import zipfile
from io import BytesIO
from datetime import datetime
import json


class AuditPackageExporter:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def create_audit_package(self, **kwargs):
        """
        Create complete audit package as ZIP file

        Args:
            kwargs: Dictionary containing:
                - urs_file_path: Path to URS document
                - test_script_docx: BytesIO of test script
                - rtm_excel: BytesIO of RTM Excel
                - rtm_word: BytesIO of RTM Word
                - validation_plan: BytesIO of VMP
                - validation_summary: BytesIO of VSR
                - quality_report: Dict of quality check results
                - change_report: Dict of change analysis results
                - test_steps: List of test steps (for metadata)
                - urs_text: Extracted URS text (for metadata)

        Returns:
            BytesIO object containing ZIP file
        """
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create folder structure
            folders = [
                '01_Requirements/',
                '02_Test_Scripts/',
                '03_Traceability/',
                '04_Validation_Docs/',
                '05_Quality_Reports/',
                '06_Metadata/'
            ]

            # Add README
            readme_content = self._generate_readme(**kwargs)
            zip_file.writestr('README.txt', readme_content)

            # 1. Requirements (URS)
            if 'urs_file_path' in kwargs and os.path.exists(kwargs['urs_file_path']):
                with open(kwargs['urs_file_path'], 'rb') as f:
                    zip_file.writestr(
                        f"01_Requirements/URS_{self.timestamp}.{kwargs.get('urs_extension', 'docx')}",
                        f.read()
                    )

            # 2. Test Scripts
            if 'test_script_docx' in kwargs and kwargs['test_script_docx']:
                kwargs['test_script_docx'].seek(0)
                zip_file.writestr(
                    f'02_Test_Scripts/Test_Script_{self.timestamp}.docx',
                    kwargs['test_script_docx'].read()
                )

            # 3. Traceability Matrix
            if 'rtm_excel' in kwargs and kwargs['rtm_excel']:
                kwargs['rtm_excel'].seek(0)
                zip_file.writestr(
                    f'03_Traceability/RTM_{self.timestamp}.xlsx',
                    kwargs['rtm_excel'].read()
                )

            if 'rtm_word' in kwargs and kwargs['rtm_word']:
                kwargs['rtm_word'].seek(0)
                zip_file.writestr(
                    f'03_Traceability/RTM_{self.timestamp}.docx',
                    kwargs['rtm_word'].read()
                )

            # 4. Validation Documents
            if 'validation_plan' in kwargs and kwargs['validation_plan']:
                kwargs['validation_plan'].seek(0)
                zip_file.writestr(
                    f'04_Validation_Docs/Validation_Plan_{self.timestamp}.docx',
                    kwargs['validation_plan'].read()
                )

            if 'validation_summary' in kwargs and kwargs['validation_summary']:
                kwargs['validation_summary'].seek(0)
                zip_file.writestr(
                    f'04_Validation_Docs/Validation_Summary_{self.timestamp}.docx',
                    kwargs['validation_summary'].read()
                )

            # 5. Quality Reports
            if 'quality_report' in kwargs and kwargs['quality_report']:
                quality_json = json.dumps(kwargs['quality_report'], indent=2)
                zip_file.writestr(
                    f'05_Quality_Reports/Quality_Check_{self.timestamp}.json',
                    quality_json
                )

                # Also create readable text version
                quality_text = self._format_quality_report(kwargs['quality_report'])
                zip_file.writestr(
                    f'05_Quality_Reports/Quality_Check_{self.timestamp}.txt',
                    quality_text
                )

            if 'change_report' in kwargs and kwargs['change_report']:
                change_json = json.dumps(kwargs['change_report'], indent=2)
                zip_file.writestr(
                    f'05_Quality_Reports/Change_Analysis_{self.timestamp}.json',
                    change_json
                )

            # 6. Metadata
            metadata = self._generate_metadata(**kwargs)
            zip_file.writestr(
                f'06_Metadata/package_metadata_{self.timestamp}.json',
                json.dumps(metadata, indent=2)
            )

        zip_buffer.seek(0)
        return zip_buffer

    def _generate_readme(self, **kwargs):
        """Generate README for audit package"""
        content = f"""
═══════════════════════════════════════════════════════════════
               VALIDATION AUDIT PACKAGE
═══════════════════════════════════════════════════════════════

Package Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Package ID: AUDIT_{self.timestamp}

═══════════════════════════════════════════════════════════════
CONTENTS
═══════════════════════════════════════════════════════════════

01_Requirements/
  - User Requirements Specification (URS)
  - Source document for all requirements

02_Test_Scripts/
  - Generated test scripts
  - Comprehensive test cases for all requirements

03_Traceability/
  - Requirements Traceability Matrix (RTM)
  - Excel and Word formats
  - Complete mapping of requirements to test cases

04_Validation_Docs/
  - Validation Master Plan (VMP)
  - Validation Summary Report (VSR)
  - GxP-compliant validation documentation

05_Quality_Reports/
  - Requirements quality analysis
  - Change impact analysis (if applicable)
  - JSON and human-readable formats

06_Metadata/
  - Package metadata and generation info
  - Timestamps and version information

═══════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════

This package contains all artifacts required for regulatory
inspection and audit purposes. All documents are generated
from the source URS and maintain full traceability.

For questions or support, refer to the package metadata.

═══════════════════════════════════════════════════════════════
COMPLIANCE
═══════════════════════════════════════════════════════════════

This package is designed to support compliance with:
- FDA 21 CFR Part 11
- EU Annex 11
- GAMP 5 guidelines
- GxP validation requirements

Always review and approve documents according to your
organization's validation procedures.

═══════════════════════════════════════════════════════════════
"""
        return content

    def _generate_metadata(self, **kwargs):
        """Generate package metadata"""
        metadata = {
            'package_id': f'AUDIT_{self.timestamp}',
            'generation_timestamp': datetime.now().isoformat(),
            'generator_version': '1.0',
            'contents': {
                'urs_included': 'urs_file_path' in kwargs,
                'test_scripts_included': 'test_script_docx' in kwargs,
                'rtm_included': 'rtm_excel' in kwargs or 'rtm_word' in kwargs,
                'validation_docs_included': 'validation_plan' in kwargs and 'validation_summary' in kwargs,
                'quality_reports_included': 'quality_report' in kwargs or 'change_report' in kwargs
            },
            'statistics': {
                'total_requirements': len(kwargs.get('test_steps', [])),
                'total_test_cases': len(kwargs.get('test_steps', [])),
                'urs_text_length': len(kwargs.get('urs_text', ''))
            }
        }

        return metadata

    def _format_quality_report(self, quality_report):
        """Format quality report as readable text"""
        if not quality_report.get('success'):
            return f"Quality Check Failed: {quality_report.get('error', 'Unknown error')}"

        text = f"""
═══════════════════════════════════════════════════════════════
           REQUIREMENTS QUALITY ANALYSIS REPORT
═══════════════════════════════════════════════════════════════

Overall Quality Score: {quality_report.get('overall_quality_score', 'N/A')}
Total Requirements: {quality_report.get('total_requirements', 'N/A')}
Issues Found: {quality_report.get('issues_found', 0)}

"""

        # Issues
        if quality_report.get('issues'):
            text += "═══════════════════════════════════════════════════════════════\n"
            text += "ISSUES IDENTIFIED\n"
            text += "═══════════════════════════════════════════════════════════════\n\n"

            for idx, issue in enumerate(quality_report['issues'], 1):
                text += f"{idx}. {issue.get('category', 'Unknown')} [{issue.get('severity', 'N/A')}]\n"
                text += f"   Requirement: {issue.get('requirement_excerpt', 'N/A')}\n"
                text += f"   Problem: {issue.get('description', 'N/A')}\n"
                text += f"   Suggestion: {issue.get('suggestion', 'N/A')}\n\n"

        # Strengths
        if quality_report.get('strengths'):
            text += "═══════════════════════════════════════════════════════════════\n"
            text += "STRENGTHS\n"
            text += "═══════════════════════════════════════════════════════════════\n\n"
            for strength in quality_report['strengths']:
                text += f"• {strength}\n"
            text += "\n"

        # Recommendations
        if quality_report.get('recommendations'):
            text += "═══════════════════════════════════════════════════════════════\n"
            text += "RECOMMENDATIONS\n"
            text += "═══════════════════════════════════════════════════════════════\n\n"
            for rec in quality_report['recommendations']:
                text += f"• {rec}\n"
            text += "\n"

        return text
