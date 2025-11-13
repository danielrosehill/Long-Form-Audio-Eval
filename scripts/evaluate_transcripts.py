#!/usr/bin/env python3
"""
Evaluation Script - Compare STT transcripts against ground truth
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import jiwer
import werpy


def load_ground_truth(config: Dict) -> str:
    """Load ground truth transcript"""
    truth_path = Path(config['source_of_truth'])
    with open(truth_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def load_transcript(run_config: Dict, base_dir: Path) -> str:
    """Load transcript for a specific run"""
    output_dir = base_dir / run_config['output_dir']
    transcript_file = output_dir / 'transcript.txt'

    if not transcript_file.exists():
        return None

    with open(transcript_file, 'r', encoding='utf-8') as f:
        return f.read().strip()


def calculate_metrics(reference: str, hypothesis: str) -> Dict:
    """Calculate WER, CER, and other metrics"""

    # Using jiwer for standard metrics
    wer = jiwer.wer(reference, hypothesis)
    cer = jiwer.cer(reference, hypothesis)

    # Calculate word-level measures
    measures = jiwer.compute_measures(reference, hypothesis)

    # Using werpy for detailed error analysis
    werpy_result = werpy.wer(reference, hypothesis)

    return {
        'wer': wer,
        'cer': cer,
        'word_accuracy': 1 - wer,
        'substitutions': measures['substitutions'],
        'deletions': measures['deletions'],
        'insertions': measures['insertions'],
        'hits': measures['hits'],
        'reference_words': len(reference.split()),
        'hypothesis_words': len(hypothesis.split()),
        'werpy_wer': werpy_result if isinstance(werpy_result, float) else None
    }


def evaluate_all_runs(config_path: str = "config/runs-config.json"):
    """Evaluate all completed runs"""

    config_path = Path(config_path)
    base_dir = config_path.parent.parent

    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Load ground truth
    print("Loading ground truth...")
    ground_truth = load_ground_truth(config)
    print(f"Ground truth: {len(ground_truth)} characters, {len(ground_truth.split())} words\n")

    # Results storage
    results = []

    # Evaluate each run
    for run in config['runs']:
        run_id = run['run_id']

        # Skip incomplete runs
        if not run.get('completed', False):
            print(f"⊘ {run_id}: Skipped (not completed)")
            continue

        # Load transcript
        transcript = load_transcript(run, base_dir)
        if transcript is None:
            print(f"⊘ {run_id}: Skipped (transcript not found)")
            continue

        print(f"Evaluating {run_id} ({run['provider']} - {run['model']})...")

        # Calculate metrics
        metrics = calculate_metrics(ground_truth, transcript)

        # Load metadata for processing time
        metadata_file = base_dir / run['output_dir'] / 'metadata.json'
        processing_time = 0
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                processing_time = metadata.get('processing_time_seconds', 0)

        # Store results
        result = {
            'run_id': run_id,
            'run_type': run['run_type'],
            'provider': run['provider'],
            'model': run['model'],
            'engine': run.get('engine', 'unknown'),
            'processing_time': processing_time,
            'metrics': metrics
        }
        results.append(result)

        # Print summary
        print(f"  WER: {metrics['wer']:.4f} ({metrics['wer']*100:.2f}%)")
        print(f"  CER: {metrics['cer']:.4f} ({metrics['cer']*100:.2f}%)")
        print(f"  Accuracy: {metrics['word_accuracy']:.4f} ({metrics['word_accuracy']*100:.2f}%)")
        print(f"  Errors: {metrics['substitutions']} subs, {metrics['deletions']} dels, {metrics['insertions']} ins")
        print()

    # Save results
    results_file = base_dir / 'evaluation_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'ground_truth_stats': {
                'characters': len(ground_truth),
                'words': len(ground_truth.split())
            },
            'results': results,
            'timestamp': __import__('time').strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2)

    print(f"\n✓ Results saved to: {results_file}")

    # Generate summary report
    generate_summary_report(results, base_dir)

    return results


def generate_summary_report(results: List[Dict], base_dir: Path):
    """Generate a human-readable summary report"""

    if not results:
        print("No results to report.")
        return

    # Sort by WER (best first)
    sorted_results = sorted(results, key=lambda x: x['metrics']['wer'])

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("SPEECH-TO-TEXT EVALUATION SUMMARY")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary table
    report_lines.append("RESULTS (sorted by WER, best first):")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Rank':<6} {'Run ID':<10} {'Provider':<15} {'Model':<20} {'WER':<10} {'CER':<10}")
    report_lines.append("-" * 80)

    for idx, result in enumerate(sorted_results, 1):
        wer_pct = result['metrics']['wer'] * 100
        cer_pct = result['metrics']['cer'] * 100
        report_lines.append(
            f"{idx:<6} {result['run_id']:<10} {result['provider']:<15} "
            f"{result['model']:<20} {wer_pct:>6.2f}%   {cer_pct:>6.2f}%"
        )

    report_lines.append("-" * 80)
    report_lines.append("")

    # Detailed breakdown
    report_lines.append("DETAILED BREAKDOWN:")
    report_lines.append("-" * 80)

    for result in sorted_results:
        metrics = result['metrics']
        report_lines.append(f"\n{result['run_id']} - {result['provider']} ({result['model']})")
        report_lines.append(f"  Type: {result['run_type']}")
        report_lines.append(f"  Word Error Rate (WER): {metrics['wer']:.4f} ({metrics['wer']*100:.2f}%)")
        report_lines.append(f"  Character Error Rate (CER): {metrics['cer']:.4f} ({metrics['cer']*100:.2f}%)")
        report_lines.append(f"  Word Accuracy: {metrics['word_accuracy']:.4f} ({metrics['word_accuracy']*100:.2f}%)")
        report_lines.append(f"  Error Breakdown:")
        report_lines.append(f"    - Substitutions: {metrics['substitutions']}")
        report_lines.append(f"    - Deletions: {metrics['deletions']}")
        report_lines.append(f"    - Insertions: {metrics['insertions']}")
        report_lines.append(f"    - Correct (Hits): {metrics['hits']}")
        report_lines.append(f"  Word Count: {metrics['hypothesis_words']} (reference: {metrics['reference_words']})")
        if result['processing_time'] > 0:
            report_lines.append(f"  Processing Time: {result['processing_time']:.2f} seconds")

    report_lines.append("")
    report_lines.append("=" * 80)

    # Print report
    report_text = '\n'.join(report_lines)
    print("\n" + report_text)

    # Save report
    report_file = base_dir / 'evaluation_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n✓ Report saved to: {report_file}")


def main():
    import sys

    config_path = "config/runs-config.json"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    evaluate_all_runs(config_path)


if __name__ == '__main__':
    main()
