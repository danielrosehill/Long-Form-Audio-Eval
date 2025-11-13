# Eden AI Integration Guide

## Overview

This project uses [Eden AI](https://www.edenai.co/) as a unified API gateway to access multiple Speech-to-Text providers through a single, standardized interface.

## Benefits

### Single SDK
Instead of managing 10+ different provider SDKs, we use one unified `edenai` package.

### Standardized Response Format
All providers return responses in the same JSON structure, making evaluation consistent.

### Easy Provider Switching
Change providers by modifying a single configuration parameter instead of rewriting code.

### Centralized Cost Tracking
Eden AI provides unified billing and cost tracking across all providers.

### GDPR Compliance
Filter to use only GDPR-compliant engines when needed.

### No Vendor Lock-in
Easily switch between providers or test multiple providers simultaneously.

## Supported Providers

Via Eden AI, this project supports the following STT providers:

| Provider | Model | Run ID | Status |
|----------|-------|--------|--------|
| **OpenAI** | whisper-1 | run-4 | Pending |
| **Deepgram** | nova-2 | run-5 | Pending |
| **AssemblyAI** | chirp | run-6 | Pending |
| **Groq** | whisper-large-v3 | run-7 | Pending |
| **Speechmatics** | enhanced | run-8 | Pending |
| **Google** | speech-to-text | run-9 | Pending |
| **Amazon** | transcribe | run-10 | Pending |
| **Microsoft** | azure-stt | run-11 | Pending |
| **Symbl.ai** | default | run-12 | Pending |
| **Gladia** | fast | run-13 | Pending |

## Setup

### 1. Install Dependencies

```bash
pip install -r config/requirements-cloud.txt
```

This installs:
- `edenai>=6.0.0` - Eden AI unified SDK
- `jiwer` and `werpy` - Evaluation metrics
- `python-dotenv` - Environment variable management

### 2. Get Eden AI API Key

1. Sign up at [https://www.edenai.co/](https://www.edenai.co/)
2. Navigate to your dashboard
3. Generate an API key
4. Add to your `.env` file:

```bash
EDENAI_API_KEY="your-eden-ai-key-here"
```

### 3. Configure Providers (Optional)

Eden AI handles provider authentication. You don't need individual provider API keys unless you're using direct integration.

## Usage

### Run Single Transcription

```bash
# Load environment and run transcription
set -a && source .env && set +a
python scripts/edenai_stt_runner.py run-4
```

### Run All Cloud Transcriptions

```bash
# Run all pending cloud STT evaluations
for run_id in run-4 run-5 run-6 run-7 run-8 run-9 run-10 run-11 run-12 run-13; do
    python scripts/edenai_stt_runner.py $run_id
done
```

### Check Available Runs

```bash
python scripts/edenai_stt_runner.py
```

## How It Works

### 1. Audio Upload
The script uploads your audio file to Eden AI's platform.

### 2. Async Processing
Eden AI submits the job to the specified provider and returns a job ID.

### 3. Polling
The script polls Eden AI's API every 5 seconds to check job status.

### 4. Results
Once complete, the transcript and metadata are downloaded and saved.

### 5. Cost Tracking
Eden AI returns the cost of the transcription, which is saved in metadata.

## Output Structure

Each run creates:

```
runs/cloud-stt/run-X/
├── transcript.txt          # Plain text transcript
└── metadata.json          # Run metadata including cost
```

### Metadata Format

```json
{
  "run_id": "run-4",
  "provider": "openai",
  "model": "whisper-1",
  "settings": {
    "language": "en",
    "temperature": 0.0
  },
  "processing_time_seconds": 45.2,
  "timestamp": "2025-11-14 14:30:00",
  "audio_file": "data/audio/podcast.mp3",
  "output_file": "runs/cloud-stt/run-4/transcript.txt",
  "via_edenai": true,
  "edenai_cost": 0.0123,
  "edenai_metadata": {
    "job_id": "abc123",
    "provider": "openai",
    "full_response": { }
  }
}
```

## Provider-Specific Notes

### OpenAI (run-4)
- Uses Whisper v2 model
- Supports temperature parameter
- Good for general English transcription

### Deepgram (run-5)
- Nova-2 model optimized for speed and accuracy
- Smart formatting and punctuation enabled
- Excellent for conversational content

### AssemblyAI (run-6)
- Universal-1 (Chirp) model
- Text formatting enabled
- Good for podcast and media content

### Groq (run-7)
- Whisper Large V3 via Groq's fast inference
- Extremely fast processing
- High accuracy on complex audio

### Speechmatics (run-8)
- Enhanced operating point for best accuracy
- Good for accents and difficult audio
- Supports 100+ languages

### Google (run-9)
- Google Cloud Speech-to-Text
- Enterprise-grade reliability
- Good for production use cases

### Amazon (run-10)
- AWS Transcribe
- Integrates with AWS ecosystem
- Automatic punctuation

### Microsoft (run-11)
- Azure Speech-to-Text
- Enterprise features
- Real-time and batch processing

### Symbl.ai (run-12)
- Conversation intelligence
- Includes sentiment and topic analysis
- Good for meetings and interviews

### Gladia (run-13)
- Fast model for quick turnaround
- 100+ language support
- Real-time and async options

## Troubleshooting

### Job Timeout
If transcription times out (10 minutes), check:
- Audio file size (large files take longer)
- Provider status on Eden AI dashboard
- Network connectivity

### API Key Issues
```bash
# Verify API key is set
echo $EDENAI_API_KEY

# If empty, reload .env
set -a && source .env && set +a
```

### Provider Errors
Check Eden AI dashboard for:
- Provider-specific errors
- Rate limits
- Account balance

## Cost Management

### Viewing Costs
All transcription costs are saved in `metadata.json` files:

```bash
# View all costs
grep -r "edenai_cost" runs/cloud-stt/*/metadata.json
```

### Estimating Costs
Eden AI provides cost estimates per minute:
- Most providers: $0.001-0.025 per minute
- Premium providers: up to $0.10 per minute

### Budget Control
Set spending limits in your Eden AI dashboard to prevent overages.

## Comparison with Direct Integration

### Direct Provider SDKs (Old Approach)
```python
# Different SDK for each provider
import openai
import deepgram
import assemblyai
# ... 10+ different imports

# Different authentication methods
openai_client = OpenAI(api_key=openai_key)
deepgram_client = Deepgram(deepgram_key)
# ... 10+ different clients

# Different API calls
openai_result = openai_client.audio.transcriptions.create(...)
deepgram_result = deepgram_client.transcription.sync_prerecorded(...)
# ... 10+ different methods
```

### Eden AI (New Approach)
```python
# Single SDK
from edenai import EdenAI

# Single authentication
client = EdenAI(api_key=edenai_key)

# Single API call
result = client.audio.speech_to_text_async(
    file=audio,
    providers='openai'  # Just change this parameter
)
```

## Migration from Direct APIs

If you were using direct provider APIs:

1. **Keep existing runs-config.json structure** - No changes needed
2. **Replace cloud_stt_runner.py** - Use edenai_stt_runner.py instead
3. **Update .env** - Add EDENAI_API_KEY, keep provider keys as backup
4. **Update requirements** - Switch to edenai package

## Advanced Usage

### Custom Settings Per Provider

```json
{
  "run_id": "run-14",
  "provider": "deepgram",
  "settings": {
    "language": "en",
    "smart_format": true,
    "diarize": true,
    "speakers": 2
  }
}
```

### GDPR-Only Providers

Filter providers in Eden AI dashboard to use only GDPR-compliant engines.

### Batch Processing

Process multiple files:

```python
for audio_file in audio_files:
    runner.run_transcription(run_id, audio_file)
```

## Resources

- [Eden AI Documentation](https://docs.edenai.co/)
- [Eden AI Speech-to-Text](https://www.edenai.co/technologies/speech)
- [Provider Comparison](https://www.edenai.co/post/best-speech-to-text-apis)
- [Pricing](https://www.edenai.co/pricing)

## Support

For issues with:
- **Eden AI platform**: Contact Eden AI support
- **This integration**: Open an issue in this repository
- **Provider-specific problems**: Check provider's status page
