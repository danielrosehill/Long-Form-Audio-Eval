#!/usr/bin/env python3
"""
Cloud STT Runner - Execute transcription using various cloud speech-to-text APIs
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Third-party imports (install as needed)
try:
    import openai
except ImportError:
    openai = None

try:
    from deepgram import Deepgram
except ImportError:
    Deepgram = None

try:
    import assemblyai as aai
except ImportError:
    aai = None

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from speechmatics.client import WebsocketClient
    from speechmatics.models import ConnectionSettings, AudioSettings
except ImportError:
    WebsocketClient = None
    ConnectionSettings = None
    AudioSettings = None


class CloudSTTRunner:
    """Execute cloud STT transcriptions based on configuration"""

    def __init__(self, config_path: str = "config/runs-config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        # Base directory is project root, not config dir
        self.base_dir = self.config_path.parent.parent

    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key from environment variables"""
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'deepgram': 'DEEPGRAM_API_KEY',
            'assemblyai': 'ASSEMBLYAI_API_KEY',
            'groq': 'GROQ_API_KEY',
            'speechmatics': 'SPEECHMATICS_API_KEY'
        }

        env_var = key_mapping.get(provider.lower())
        if not env_var:
            return None

        api_key = os.getenv(env_var)
        if not api_key:
            print(f"Warning: {env_var} not found in environment")
        return api_key

    def transcribe_openai(self, audio_path: Path, settings: Dict) -> str:
        """Transcribe using OpenAI Whisper API"""
        if openai is None:
            raise ImportError("openai package not installed. Run: pip install openai")

        api_key = self._get_api_key('openai')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        client = openai.OpenAI(api_key=api_key)

        with open(audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=settings.get('language', 'en'),
                temperature=settings.get('temperature', 0.0)
            )

        return transcript.text

    def transcribe_deepgram(self, audio_path: Path, settings: Dict) -> str:
        """Transcribe using Deepgram API"""
        if Deepgram is None:
            raise ImportError("deepgram-sdk package not installed. Run: pip install deepgram-sdk")

        api_key = self._get_api_key('deepgram')
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY not set")

        # Implementation would go here
        # Note: Deepgram SDK varies by version, this is a placeholder
        raise NotImplementedError("Deepgram integration pending")

    def transcribe_assemblyai(self, audio_path: Path, settings: Dict) -> str:
        """Transcribe using AssemblyAI API"""
        if aai is None:
            raise ImportError("assemblyai package not installed. Run: pip install assemblyai")

        api_key = self._get_api_key('assemblyai')
        if not api_key:
            raise ValueError("ASSEMBLYAI_API_KEY not set")

        aai.settings.api_key = api_key

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(str(audio_path))

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription failed: {transcript.error}")

        return transcript.text

    def transcribe_groq(self, audio_path: Path, settings: Dict) -> str:
        """Transcribe using Groq API"""
        if Groq is None:
            raise ImportError("groq package not installed. Run: pip install groq")

        api_key = self._get_api_key('groq')
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        client = Groq(api_key=api_key)

        with open(audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=settings.get('language', 'en'),
                temperature=settings.get('temperature', 0.0)
            )

        return transcript.text

    def transcribe_speechmatics(self, audio_path: Path, settings: Dict) -> str:
        """Transcribe using Speechmatics API"""
        if WebsocketClient is None:
            raise ImportError("speechmatics-python package not installed. Run: pip install speechmatics-python")

        api_key = self._get_api_key('speechmatics')
        if not api_key:
            raise ValueError("SPEECHMATICS_API_KEY not set")

        # Collect transcript text
        transcript_parts = []

        def transcript_handler(msg):
            """Handle transcript messages"""
            if 'results' in msg and len(msg['results']) > 0:
                result = msg['results'][0]
                if 'alternatives' in result and len(result['alternatives']) > 0:
                    transcript_parts.append(result['alternatives'][0]['content'])

        # Configure connection
        conn_settings = ConnectionSettings(
            url="wss://eu2.rt.speechmatics.com/v2",
            auth_token=api_key
        )

        # Configure audio
        audio_settings = AudioSettings()

        # Configure transcription
        conf = {
            "type": "transcription",
            "transcription_config": {
                "language": settings.get('language', 'en'),
                "operating_point": settings.get('operating_point', 'enhanced'),
                "enable_partials": settings.get('enable_partials', False)
            }
        }

        # Run transcription
        with WebsocketClient(conn_settings) as ws_client:
            ws_client.add_event_handler('AddTranscript', transcript_handler)
            ws_client.run_synchronously(str(audio_path), conf, audio_settings)

        return ' '.join(transcript_parts)

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

        # Execute transcription based on provider
        provider = run_config['provider'].lower()
        settings = run_config.get('settings', {})

        try:
            if provider == 'openai':
                transcript = self.transcribe_openai(audio_path, settings)
            elif provider == 'deepgram':
                transcript = self.transcribe_deepgram(audio_path, settings)
            elif provider == 'assemblyai':
                transcript = self.transcribe_assemblyai(audio_path, settings)
            elif provider == 'groq':
                transcript = self.transcribe_groq(audio_path, settings)
            elif provider == 'speechmatics':
                transcript = self.transcribe_speechmatics(audio_path, settings)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Calculate processing time
            processing_time = time.time() - start_time

            # Save transcript
            output_file = output_dir / "transcript.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcript)

            # Save metadata
            metadata = {
                'run_id': run_id,
                'provider': provider,
                'model': run_config['model'],
                'settings': settings,
                'processing_time_seconds': processing_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'audio_file': str(audio_path),
                'output_file': str(output_file)
            }

            metadata_file = output_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            print(f"\n✓ Transcription completed in {processing_time:.2f} seconds")
            print(f"  Output: {output_file}")
            print(f"  Metadata: {metadata_file}")

            # Update config to mark as completed
            run_config['completed'] = True
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

        except Exception as e:
            print(f"\n✗ Transcription failed: {e}")
            raise


def main():
    if len(sys.argv) < 2:
        print("Usage: python cloud_stt_runner.py <run_id>")
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

    runner = CloudSTTRunner()
    runner.run_transcription(run_id)


if __name__ == '__main__':
    main()
