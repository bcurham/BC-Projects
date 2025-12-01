"""
Change Control Impact Analyzer
Detects changes between URS versions and analyzes impact on test cases
"""

import os
import json
import difflib
from datetime import datetime


class ChangeAnalyzer:
    def __init__(self, baselines_folder='baselines'):
        self.baselines_folder = baselines_folder
        os.makedirs(baselines_folder, exist_ok=True)

    def save_baseline(self, urs_text, test_steps, project_name="default"):
        """
        Save current URS and test steps as baseline for future comparison

        Args:
            urs_text: Extracted URS text
            test_steps: Generated test steps
            project_name: Project identifier

        Returns:
            baseline_id: Unique identifier for this baseline
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        baseline_id = f"{project_name}_{timestamp}"

        baseline_data = {
            'baseline_id': baseline_id,
            'project_name': project_name,
            'timestamp': timestamp,
            'urs_text': urs_text,
            'test_steps': test_steps,
            'requirements_count': len(test_steps)
        }

        baseline_path = os.path.join(self.baselines_folder, f"{baseline_id}.json")

        with open(baseline_path, 'w', encoding='utf-8') as f:
            json.dump(baseline_data, f, indent=2)

        print(f"✓ Baseline saved: {baseline_id}")
        return baseline_id

    def get_latest_baseline(self, project_name="default"):
        """
        Get the most recent baseline for a project

        Args:
            project_name: Project identifier

        Returns:
            baseline_data or None if no baseline exists
        """
        baselines = [f for f in os.listdir(self.baselines_folder)
                     if f.startswith(project_name) and f.endswith('.json')]

        if not baselines:
            return None

        # Sort by timestamp (filename format ensures chronological order)
        baselines.sort(reverse=True)
        latest = baselines[0]

        baseline_path = os.path.join(self.baselines_folder, latest)
        with open(baseline_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def analyze_changes(self, new_urs_text, new_test_steps, project_name="default"):
        """
        Compare new URS against baseline and identify changes

        Args:
            new_urs_text: New URS text
            new_test_steps: New test steps
            project_name: Project identifier

        Returns:
            change_report: Dictionary containing analysis results
        """
        baseline = self.get_latest_baseline(project_name)

        if not baseline:
            return {
                'has_baseline': False,
                'message': 'No baseline found. This will be saved as the first baseline.',
                'is_first_version': True
            }

        # Analyze text-level changes
        text_diff = self._analyze_text_changes(baseline['urs_text'], new_urs_text)

        # Analyze requirement-level changes
        req_changes = self._analyze_requirement_changes(
            baseline['test_steps'],
            new_test_steps
        )

        # Determine impact
        impact_analysis = self._analyze_impact(req_changes)

        change_report = {
            'has_baseline': True,
            'baseline_id': baseline['baseline_id'],
            'baseline_timestamp': baseline['timestamp'],
            'is_first_version': False,
            'text_changes': text_diff,
            'requirement_changes': req_changes,
            'impact_analysis': impact_analysis,
            'summary': self._generate_summary(req_changes, impact_analysis)
        }

        return change_report

    def _analyze_text_changes(self, old_text, new_text):
        """Analyze text-level differences"""
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))

        return {
            'total_changes': len([line for line in diff if line.startswith('+') or line.startswith('-')]),
            'has_changes': len(diff) > 0
        }

    def _analyze_requirement_changes(self, old_steps, new_steps):
        """Analyze requirement-level changes"""
        old_req_ids = {step['requirement_id']: step for step in old_steps}
        new_req_ids = {step['requirement_id']: step for step in new_steps}

        added = [req_id for req_id in new_req_ids if req_id not in old_req_ids]
        removed = [req_id for req_id in old_req_ids if req_id not in new_req_ids]

        modified = []
        for req_id in old_req_ids:
            if req_id in new_req_ids:
                old_step = old_req_ids[req_id]
                new_step = new_req_ids[req_id]

                if (old_step['description'] != new_step['description'] or
                        old_step['expected_result'] != new_step['expected_result']):
                    modified.append({
                        'requirement_id': req_id,
                        'old_description': old_step['description'],
                        'new_description': new_step['description'],
                        'old_expected': old_step['expected_result'],
                        'new_expected': new_step['expected_result']
                    })

        return {
            'added': added,
            'removed': removed,
            'modified': modified,
            'unchanged': [req_id for req_id in old_req_ids
                          if req_id in new_req_ids and req_id not in [m['requirement_id'] for m in modified]]
        }

    def _analyze_impact(self, req_changes):
        """Analyze impact on test cases"""
        total_added = len(req_changes['added'])
        total_removed = len(req_changes['removed'])
        total_modified = len(req_changes['modified'])
        total_unchanged = len(req_changes['unchanged'])

        # Determine test cases that need action
        tests_to_add = total_added
        tests_to_remove = total_removed
        tests_to_update = total_modified
        tests_to_reuse = total_unchanged

        impact_level = 'LOW'
        if total_added + total_removed + total_modified > 10:
            impact_level = 'HIGH'
        elif total_added + total_removed + total_modified > 5:
            impact_level = 'MEDIUM'

        return {
            'impact_level': impact_level,
            'tests_to_add': tests_to_add,
            'tests_to_remove': tests_to_remove,
            'tests_to_update': tests_to_update,
            'tests_to_reuse': tests_to_reuse,
            'total_test_cases': tests_to_add + tests_to_update + tests_to_reuse
        }

    def _generate_summary(self, req_changes, impact_analysis):
        """Generate human-readable summary"""
        summary = []

        if req_changes['added']:
            summary.append(f"• {len(req_changes['added'])} new requirement(s) added")

        if req_changes['removed']:
            summary.append(f"• {len(req_changes['removed'])} requirement(s) removed")

        if req_changes['modified']:
            summary.append(f"• {len(req_changes['modified'])} requirement(s) modified")

        if req_changes['unchanged']:
            summary.append(f"• {len(req_changes['unchanged'])} requirement(s) unchanged")

        summary.append(f"\nImpact Level: {impact_analysis['impact_level']}")
        summary.append(f"Test Cases to Add: {impact_analysis['tests_to_add']}")
        summary.append(f"Test Cases to Update: {impact_analysis['tests_to_update']}")
        summary.append(f"Test Cases to Reuse: {impact_analysis['tests_to_reuse']}")

        return "\n".join(summary)
