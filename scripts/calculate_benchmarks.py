#!/usr/bin/env python3
"""
Calculate benchmark metrics (WER, CER, Word Accuracy) for STT transcripts
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import jiwer


def load_text(file_path: str) -> str:
    """Load and normalize text from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    return text


def calculate_metrics(reference: str, hypothesis: str) -> Dict[str, float]:
    """Calculate WER, CER, and Word Accuracy"""

    # Calculate WER (Word Error Rate)
    wer_value = jiwer.wer(reference, hypothesis)

    # Calculate CER (Character Error Rate)
    cer_value = jiwer.cer(reference, hypothesis)

    # Calculate Word Accuracy (100 - WER%)
    word_accuracy = max(0, 1 - wer_value) * 100

    # Get word-level stats using process_words
    output = jiwer.process_words(reference, hypothesis)

    return {
        'wer': round(wer_value * 100, 2),  # as percentage
        'cer': round(cer_value * 100, 2),  # as percentage
        'word_accuracy': round(word_accuracy, 2),  # as percentage
        'insertions': output.insertions,
        'deletions': output.deletions,
        'substitutions': output.substitutions,
        'hits': output.hits
    }


def find_transcript_file(run_dir: Path) -> Path:
    """Find the transcript file in a run directory"""
    # Look for transcript.txt first
    transcript_path = run_dir / "transcript.txt"
    if transcript_path.exists():
        return transcript_path

    # Look for any .txt file
    txt_files = list(run_dir.glob("*.txt"))
    if txt_files:
        return txt_files[0]

    raise FileNotFoundError(f"No transcript file found in {run_dir}")


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    inference_dir = base_dir / "data" / "inference"
    runs_config_path = inference_dir / "runs-config.json"
    ground_truth_path = base_dir / "data" / "ground-truth" / "truth_1.txt"

    # Load runs config
    with open(runs_config_path, 'r') as f:
        config = json.load(f)

    # Load ground truth
    print(f"Loading ground truth from: {ground_truth_path}")
    reference_text = load_text(str(ground_truth_path))
    print(f"Ground truth loaded: {len(reference_text)} characters, {len(reference_text.split())} words\n")

    # Results storage
    results = []

    # Process each run
    for run in config['runs']:
        run_id = run['run_id']

        # Skip incomplete runs
        if not run.get('completed', False):
            print(f"Skipping {run_id} - not completed")
            continue

        # Construct run directory path
        run_dir = inference_dir / run['output_dir']

        # Check if directory exists
        if not run_dir.exists():
            print(f"Skipping {run_id} - directory not found: {run_dir}")
            continue

        try:
            # Find transcript file
            transcript_path = find_transcript_file(run_dir)

            # Load hypothesis text
            hypothesis_text = load_text(str(transcript_path))

            # Calculate metrics
            metrics = calculate_metrics(reference_text, hypothesis_text)

            # Store results
            result = {
                'run_id': run_id,
                'run_type': run['run_type'],
                'provider': run['provider'],
                'model': run['model'],
                'engine': run['engine'],
                'metrics': metrics
            }
            results.append(result)

            print(f"✓ {run_id} ({run['provider']} - {run['model']})")
            print(f"  WER: {metrics['wer']}%")
            print(f"  CER: {metrics['cer']}%")
            print(f"  Word Accuracy: {metrics['word_accuracy']}%")
            print()

        except Exception as e:
            print(f"✗ Error processing {run_id}: {e}")
            continue

    # Save results
    output_path = inference_dir / "benchmark_results.json"
    with open(output_path, 'w') as f:
        json.dump({
            'ground_truth_file': str(ground_truth_path),
            'total_runs_evaluated': len(results),
            'results': results
        }, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_path}")
    print(f"Total runs evaluated: {len(results)}")
    print(f"{'='*60}\n")

    # Generate summary comparison
    print("\nSUMMARY - Sorted by Word Accuracy (Best to Worst)")
    print(f"{'='*80}")
    print(f"{'Rank':<6} {'Provider':<15} {'Model':<20} {'WER %':<10} {'Accuracy %':<12}")
    print(f"{'-'*80}")

    # Sort by word accuracy (descending)
    sorted_results = sorted(results, key=lambda x: x['metrics']['word_accuracy'], reverse=True)

    for idx, result in enumerate(sorted_results, 1):
        provider = result['provider']
        model = result['model']
        wer = result['metrics']['wer']
        accuracy = result['metrics']['word_accuracy']

        print(f"{idx:<6} {provider:<15} {model:<20} {wer:<10.2f} {accuracy:<12.2f}")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
