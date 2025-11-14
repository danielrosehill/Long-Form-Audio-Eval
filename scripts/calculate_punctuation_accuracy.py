#!/usr/bin/env python3
"""
Calculate punctuation accuracy for STT transcripts
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


def extract_punctuation_context(text: str, context_words: int = 2) -> List[Tuple[str, str]]:
    """
    Extract punctuation marks with surrounding word context.
    Returns list of (context, punctuation) tuples.
    """
    # Common sentence-ending and mid-sentence punctuation
    punctuation_marks = ['.', '!', '?', ',', ';', ':', '-', '—']

    results = []
    words = text.split()

    # Rebuild text to find punctuation positions
    for i, word in enumerate(words):
        for punct in punctuation_marks:
            if punct in word:
                # Get context: previous and next words
                context_before = ' '.join(words[max(0, i-context_words):i])
                context_after = ' '.join(words[i+1:min(len(words), i+context_words+1)])

                # Remove punctuation from the word itself for context
                word_clean = ''.join(c for c in word if c.isalnum() or c.isspace())

                context = f"{context_before} {word_clean} {context_after}".strip()
                results.append((context.lower(), punct))

    return results


def count_punctuation(text: str) -> Dict[str, int]:
    """Count occurrences of each punctuation mark"""
    punctuation_marks = ['.', '!', '?', ',', ';', ':', '-', '—', '"', "'"]
    counts = Counter()

    for char in text:
        if char in punctuation_marks:
            counts[char] += 1

    return dict(counts)


def calculate_punctuation_metrics(reference: str, hypothesis: str) -> Dict:
    """
    Calculate punctuation-specific metrics:
    - Punctuation mark precision/recall
    - Total punctuation count comparison
    - Context-aware punctuation accuracy
    """

    # Count punctuation marks
    ref_counts = count_punctuation(reference)
    hyp_counts = count_punctuation(hypothesis)

    # Total punctuation
    total_ref_punct = sum(ref_counts.values())
    total_hyp_punct = sum(hyp_counts.values())

    # Calculate per-mark accuracy
    mark_accuracy = {}
    for mark in set(list(ref_counts.keys()) + list(hyp_counts.keys())):
        ref_count = ref_counts.get(mark, 0)
        hyp_count = hyp_counts.get(mark, 0)

        if ref_count == 0:
            accuracy = 100.0 if hyp_count == 0 else 0.0
        else:
            # Accuracy as percentage of how close the counts are
            accuracy = max(0, 100 - (abs(ref_count - hyp_count) / ref_count * 100))

        mark_accuracy[mark] = {
            'reference_count': ref_count,
            'hypothesis_count': hyp_count,
            'count_accuracy': round(accuracy, 2)
        }

    # Context-aware matching
    ref_punct_context = extract_punctuation_context(reference)
    hyp_punct_context = extract_punctuation_context(hypothesis)

    # Create lookup dictionaries
    ref_dict = {}
    for context, punct in ref_punct_context:
        if context not in ref_dict:
            ref_dict[context] = []
        ref_dict[context].append(punct)

    hyp_dict = {}
    for context, punct in hyp_punct_context:
        if context not in hyp_dict:
            hyp_dict[context] = []
        hyp_dict[context].append(punct)

    # Match punctuation in similar contexts
    matched_contexts = 0
    total_contexts = len(ref_dict)

    for context, ref_puncts in ref_dict.items():
        if context in hyp_dict:
            hyp_puncts = hyp_dict[context]
            # Check if punctuation matches
            if ref_puncts == hyp_puncts:
                matched_contexts += 1

    context_accuracy = (matched_contexts / total_contexts * 100) if total_contexts > 0 else 0

    # Overall punctuation density
    ref_words = len(reference.split())
    hyp_words = len(hypothesis.split())

    ref_density = (total_ref_punct / ref_words * 100) if ref_words > 0 else 0
    hyp_density = (total_hyp_punct / hyp_words * 100) if hyp_words > 0 else 0

    return {
        'total_punctuation': {
            'reference': total_ref_punct,
            'hypothesis': total_hyp_punct,
            'difference': total_hyp_punct - total_ref_punct
        },
        'punctuation_density': {
            'reference_percent': round(ref_density, 2),
            'hypothesis_percent': round(hyp_density, 2)
        },
        'mark_accuracy': mark_accuracy,
        'context_match_accuracy': round(context_accuracy, 2),
        'overall_punctuation_score': round(
            (context_accuracy * 0.7 +
             (100 - abs(ref_density - hyp_density) / max(ref_density, 0.01) * 100) * 0.3),
            2
        )
    }


def load_text(file_path: str) -> str:
    """Load text from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def find_transcript_file(run_dir: Path) -> Path:
    """Find the transcript file in a run directory"""
    transcript_path = run_dir / "transcript.txt"
    if transcript_path.exists():
        return transcript_path

    txt_files = list(run_dir.glob("*.txt"))
    if txt_files:
        return txt_files[0]

    raise FileNotFoundError(f"No transcript file found in {run_dir}")


def main():
    base_dir = Path(__file__).parent.parent
    inference_dir = base_dir / "data" / "inference"
    runs_config_path = inference_dir / "runs-config.json"
    ground_truth_path = base_dir / "data" / "ground-truth" / "truth_1.txt"

    # Load configuration
    with open(runs_config_path, 'r') as f:
        config = json.load(f)

    # Load ground truth
    print(f"Loading ground truth from: {ground_truth_path}")
    reference_text = load_text(str(ground_truth_path))

    ref_punct_count = sum(count_punctuation(reference_text).values())
    print(f"Ground truth: {len(reference_text.split())} words, {ref_punct_count} punctuation marks\n")

    results = []

    # Process each run
    for run in config['runs']:
        run_id = run['run_id']

        if not run.get('completed', False):
            print(f"Skipping {run_id} - not completed")
            continue

        run_dir = inference_dir / run['output_dir']

        if not run_dir.exists():
            print(f"Skipping {run_id} - directory not found")
            continue

        try:
            transcript_path = find_transcript_file(run_dir)
            hypothesis_text = load_text(str(transcript_path))

            metrics = calculate_punctuation_metrics(reference_text, hypothesis_text)

            result = {
                'run_id': run_id,
                'provider': run['provider'],
                'model': run['model'],
                'metrics': metrics
            }
            results.append(result)

            print(f"✓ {run_id} ({run['provider']} - {run['model']})")
            print(f"  Overall Punctuation Score: {metrics['overall_punctuation_score']}%")
            print(f"  Context Match Accuracy: {metrics['context_match_accuracy']}%")
            print(f"  Total Punctuation: {metrics['total_punctuation']['hypothesis']} (ref: {metrics['total_punctuation']['reference']})")
            print()

        except Exception as e:
            print(f"✗ Error processing {run_id}: {e}")
            continue

    # Save results
    output_path = inference_dir / "punctuation_results.json"
    with open(output_path, 'w') as f:
        json.dump({
            'ground_truth_file': str(ground_truth_path),
            'total_runs_evaluated': len(results),
            'results': results
        }, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Results saved to: {output_path}")
    print(f"Total runs evaluated: {len(results)}")
    print(f"{'='*70}\n")

    # Summary
    print("\nPUNCTUATION ACCURACY RANKINGS")
    print(f"{'='*80}")
    print(f"{'Rank':<6} {'Provider':<15} {'Model':<25} {'Score %':<10}")
    print(f"{'-'*80}")

    sorted_results = sorted(results, key=lambda x: x['metrics']['overall_punctuation_score'], reverse=True)

    for idx, result in enumerate(sorted_results, 1):
        provider = result['provider']
        model = result['model']
        score = result['metrics']['overall_punctuation_score']

        print(f"{idx:<6} {provider:<15} {model:<25} {score:<10.2f}")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
