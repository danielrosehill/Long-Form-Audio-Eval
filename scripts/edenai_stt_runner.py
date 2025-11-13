#!/usr/bin/env python3
"""
Eden AI STT Runner - Execute transcription using Eden AI's unified API
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import requests


class EdenAISTTRunner:
    """Execute STT transcriptions via Eden AI unified API"""

    # Provider name mapping: config name -> Eden AI provider name
    PROVIDER_MAPPING = {
        'openai': 'openai',
        'deepgram': 'deepgram',
        'assemblyai': 'assemblyai',
        'speechmatics': 'speechmatics',
        'google': 'google',
        'amazon': 'amazon',
        'microsoft': 'microsoft',
        'symbl': 'symbl',
        'gladia': 'gladia',
        'groq': 'openai'  # Groq uses OpenAI's Whisper model
    }

    def __init__(self, config_path: str = "config/runs-config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.base_dir = self.config_path.parent.parent

        # Get Eden AI API key
        self.api_key = os.getenv('EDEN_API_KEY')
        if not self.api_key:
            raise ValueError("EDEN_API_KEY not set in environment")

        self.api_url = "https://api.edenai.run/v2/audio/speech_to_text_async"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "multipart/form-data"
        }

    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _get_edenai_provider(self, provider: str) -> str:
        """Map config provider name to Eden AI provider name"""
        return self.PROVIDER_MAPPING.get(provider.lower(), provider.lower())

    def transcribe_audio(self, audio_path: Path, provider: str, settings: Dict) -> Dict:
        """
        Transcribe audio using Eden AI REST API

        Returns dict with:
        - text: transcription text
        - cost: transcription cost (if available)
        - metadata: additional provider-specific data
        """
        edenai_provider = self._get_edenai_provider(provider)

        print(f"  Using Eden AI provider: {edenai_provider}")

        # Prepare form data
        language = settings.get('language', settings.get('language_code', 'en'))

        # Submit job
        try:
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                data = {
                    'providers': edenai_provider,
                    'language': language
                }

                # Remove Content-Type header to let requests set it with boundary
                headers = {"Authorization": f"Bearer {self.api_key}"}

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=data,
                    files=files
                )

                response.raise_for_status()
                result = response.json()

            # Get job ID
            job_id = result.get('public_id')
            if not job_id:
                raise Exception(f"No job ID returned. Response: {result}")

            print(f"  Job submitted: {job_id}")
            print(f"  Waiting for transcription to complete...")

            # Poll for completion
            status_url = f"https://api.edenai.run/v2/audio/speech_to_text_async/{job_id}"
            max_attempts = 120  # 10 minutes with 5-second intervals

            for attempt in range(max_attempts):
                time.sleep(5)

                status_response = requests.get(
                    status_url,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                status_response.raise_for_status()
                status = status_response.json()

                current_status = status.get('status')

                if current_status == 'finished':
                    # Get provider results
                    provider_results = status.get('results', {}).get(edenai_provider, {})

                    text = provider_results.get('text', '')
                    if not text:
                        raise Exception(f"No text in results: {provider_results}")

                    return {
                        'text': text,
                        'cost': provider_results.get('cost'),
                        'metadata': {
                            'job_id': job_id,
                            'provider': edenai_provider,
                            'full_response': provider_results
                        }
                    }
                elif current_status == 'failed':
                    error = status.get('error', status.get('results', {}).get(edenai_provider, {}).get('error', 'Unknown error'))
                    raise Exception(f"Transcription failed: {error}")

                # Print progress
                if attempt % 6 == 0:  # Every 30 seconds
                    print(f"  Still processing... ({attempt * 5}s elapsed, status: {current_status})")

            raise Exception("Transcription timed out after 10 minutes")

        except requests.exceptions.RequestException as e:
            print(f"  API request error: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"  Error during transcription: {e}")
            raise

    def run_transcription(self, run_id: str) -> None:
        """Execute transcription for a specific run"""
        # Find run configuration
        run_config = None
        for run in self.config['runs']:
            if run['run_id'] == run_id:
                run_config = run
                break

        if not run_config:
            raise ValueError(f"Run {run_id} not found in configuration")

        if run_config.get('completed'):
            print(f"Run {run_id} already completed. Skipping.")
            return

        if run_config['run_type'] != 'cloud-stt':
            print(f"Run {run_id} is not a cloud STT run. Skipping.")
            return

        print(f"\n{'='*60}")
        print(f"Running: {run_id}")
        print(f"Provider: {run_config['provider']}")
        print(f"Model: {run_config['model']}")
        print(f"Via: Eden AI unified API")
        print(f"{'='*60}\n")

        # Get audio file path
        audio_path = self.base_dir / self.config['source_audio']
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Create output directory
        output_dir = self.base_dir / run_config['output_dir']
        output_dir.mkdir(parents=True, exist_ok=True)

        # Start timing
        start_time = time.time()

        # Execute transcription
        provider = run_config['provider']
        settings = run_config.get('settings', {})

        try:
            result = self.transcribe_audio(audio_path, provider, settings)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Save transcript
            output_file = output_dir / "transcript.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])

            # Save metadata
            metadata = {
                'run_id': run_id,
                'provider': provider,
                'model': run_config['model'],
                'settings': settings,
                'processing_time_seconds': processing_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'audio_file': str(audio_path),
                'output_file': str(output_file),
                'via_edenai': True,
                'edenai_cost': result.get('cost'),
                'edenai_metadata': result.get('metadata')
            }

            metadata_file = output_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            print(f"\n✓ Transcription completed in {processing_time:.2f} seconds")
            print(f"  Output: {output_file}")
            print(f"  Metadata: {metadata_file}")
            if result.get('cost'):
                print(f"  Cost: ${result['cost']:.4f}")

            # Update config to mark as completed
            run_config['completed'] = True
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

        except Exception as e:
            print(f"\n✗ Transcription failed: {e}")
            raise


def main():
    if len(sys.argv) < 2:
        print("Usage: python edenai_stt_runner.py <run_id>")
        print("\nAvailable cloud runs:")

        config_path = Path("config/runs-config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            for run in config['runs']:
                if run['run_type'] == 'cloud-stt':
                    status = "✓ completed" if run.get('completed') else "○ pending"
                    print(f"  {run['run_id']}: {run['provider']} - {run['model']} [{status}]")

        sys.exit(1)

    run_id = sys.argv[1]

    runner = EdenAISTTRunner()
    runner.run_transcription(run_id)


if __name__ == '__main__':
    main()
