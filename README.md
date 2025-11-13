# Long-Form Audio Evaluation

A framework for evaluating speech-to-text (STT) models on long-form audio content, comparing both local and cloud-based transcription services.

## Directory Structure

```
.
├── config/                      # Configuration files
│   ├── runs-config.json        # Run configurations for all STT evaluations
│   └── requirements-cloud.txt  # Python dependencies for cloud APIs
├── data/                       # Data files
│   ├── audio/                  # Source audio files
│   │   └── podcast.mp3        # Test audio file
│   └── ground-truth/          # Reference transcripts
│       ├── truth_1.txt        # Plain text ground truth
│       └── truth_1.srt        # SRT format ground truth
├── docs/                       # Documentation
│   └── to-test.md             # Models and services to evaluate
├── runs/                       # Transcription outputs
│   ├── local-stt/             # Local model runs
│   │   ├── run-1/
│   │   ├── run-2/
│   │   └── run-3/
│   └── cloud-stt/             # Cloud API runs
│       ├── run-4/
│       ├── run-5/
│       ├── run-6/
│       └── run-7/
└── scripts/                    # Utility scripts
    ├── cloud_stt_runner.py    # Cloud STT execution script
    └── srt_to_text.py         # SRT to plain text converter
```

## Runs Configuration

All evaluation runs are defined in [config/runs-config.json](config/runs-config.json). Each run includes:

- **run_id**: Unique identifier (run-1, run-2, etc.)
- **run_type**: `local-stt` or `cloud-stt`
- **model**: Model name/identifier
- **provider**: Service provider (OpenAI, Deepgram, AssemblyAI, Groq, or local)
- **settings**: Model-specific configuration
- **output_dir**: Location for transcription outputs
- **completed**: Status flag

### Local Runs (Completed)

1. **run-1**: Whisper Base (local, English specified)
2. **run-2**: Whisper Tiny (local, English specified)
3. **run-3**: Whisper Base (local, auto-detect language)

### Cloud Runs (Pending)

4. **run-4**: OpenAI Whisper API
5. **run-5**: Deepgram Nova-2
6. **run-6**: AssemblyAI Universal-1 (Chirp)
7. **run-7**: Groq Whisper Large V3

## Setup

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- API keys for cloud services (if running cloud evaluations)

### Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install cloud dependencies
pip install -r config/requirements-cloud.txt
```

### API Keys

Set the following environment variables for cloud services:

```bash
export OPENAI_API_KEY="your-key-here"
export GROQ_API_KEY="your-key-here"
export ASSEMBLYAI_API_KEY="your-key-here"
export DEEPGRAM_API_KEY="your-key-here"
```

Alternatively, create a `.env` file in the project root.

## Usage

### Running Cloud Transcriptions

```bash
# Run a single evaluation
python scripts/cloud_stt_runner.py run-4

# List available runs
python scripts/cloud_stt_runner.py
```

### Converting SRT to Plain Text

```bash
# Convert with automatic output naming
python scripts/srt_to_text.py path/to/file.srt

# Specify output file
python scripts/srt_to_text.py path/to/file.srt output.txt
```

## Output Format

Each run generates:

- **transcript.txt**: Plain text transcription
- **transcript.srt**: SRT format (for local runs)
- **metadata.json**: Run metadata including processing time and settings

## Evaluation Metrics

Planned metrics (to be implemented):

- Word Error Rate (WER)
- Character Error Rate (CER)
- Word Accuracy
- Processing Time
- Cost per minute

## Adding New Runs

Edit [config/runs-config.json](config/runs-config.json) and add a new run configuration:

```json
{
  "run_id": "run-8",
  "run_type": "cloud-stt",
  "model": "your-model",
  "provider": "provider-name",
  "engine": "api",
  "settings": {
    "language": "en"
  },
  "output_dir": "runs/cloud-stt/run-8",
  "completed": false,
  "notes": "Description of this run"
}
```

## License

[Add license information]

## Contributing

[Add contribution guidelines]
