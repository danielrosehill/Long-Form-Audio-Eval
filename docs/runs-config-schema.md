# runs-config.json Schema Documentation

## Overview

The `runs-config.json` file defines all STT transcription runs, their configurations, and evaluation parameters.

## Top-Level Structure

```json
{
  "runs": [/* array of run objects */],
  "source_audio": "string",
  "source_of_truth": "string",
  "evaluation_metrics": ["string"]
}
```

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `runs` | Array | Yes | Array of run configuration objects |
| `source_audio` | String | Yes | Path to source audio file (relative to project root) |
| `source_of_truth` | String | Yes | Path to ground truth transcript (relative to project root) |
| `evaluation_metrics` | Array | Yes | List of metrics to calculate: "wer", "cer", "word_accuracy", "processing_time", "cost" |

## Run Object Schema

Each object in the `runs` array has the following structure:

```json
{
  "run_id": "run-X",
  "run_type": "local-stt|cloud-stt",
  "model": "string",
  "provider": "string",
  "inference_provider": "string",
  "engine": "string",
  "run_method": {},
  "settings": {},
  "output_dir": "string",
  "completed": boolean,
  "notes": "string",
  "run_notes": {}
}
```

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `run_id` | String | Yes | Unique identifier (e.g., "run-1", "run-2") |
| `run_type` | String | Yes | Either "local-stt" or "cloud-stt" |
| `model` | String | Yes | Model name/identifier |
| `provider` | String | Yes | Service provider (openai, deepgram, assemblyai, groq, speechmatics, local) |
| `inference_provider` | String | No | Inference platform if accessed via third-party (e.g., "huggingface", "replicate", "together") |
| `engine` | String | Yes | Execution engine (api, Buzz, manual) |
| `run_method` | Object | No | How the run was executed (web-ui, api, cli, etc.) |
| `settings` | Object | Yes | Provider-specific configuration |
| `output_dir` | String | Yes | Path to output directory (relative to project root) |
| `completed` | Boolean | Yes | Whether transcription has been completed |
| `notes` | String | No | Human-readable description of the run |
| `run_notes` | Object | No | Structured annotations about run parameters |

## Run Method Schema

The `run_method` object describes how the transcription was executed:

```json
{
  "run_method": {
    "interface": "web-ui|api|cli|gui|manual",
    "automation": "automated|manual",
    "description": "string"
  }
}
```

### Run Method Fields

| Field | Type | Description |
|-------|------|-------------|
| `interface` | String | How the run was executed: "web-ui", "api", "cli", "gui", "manual" |
| `automation` | String | Whether run was automated via script or manual |
| `description` | String | Optional description of the execution method |

### Run Method Examples

**API via Script (Automated):**
```json
"run_method": {
  "interface": "api",
  "automation": "automated",
  "description": "Executed via cloud_stt_runner.py script"
}
```

**Web UI (Manual):**
```json
"run_method": {
  "interface": "web-ui",
  "automation": "manual",
  "description": "Uploaded to provider web interface"
}
```

**Desktop GUI (Manual):**
```json
"run_method": {
  "interface": "gui",
  "automation": "manual",
  "description": "Processed using Buzz desktop application"
}
```

## Inference Provider

The `inference_provider` field is used when accessing models through third-party inference platforms:

| Inference Provider | Use Case | Example |
|-------------------|----------|---------|
| `huggingface` | Accessing models via Hugging Face Inference API | Whisper via HF Inference |
| `replicate` | Running models on Replicate | Any model on Replicate platform |
| `together` | Using Together AI inference | Models via Together AI |
| `runpod` | RunPod serverless inference | Custom deployments |
| `direct` | Direct API from model provider | OpenAI, Deepgram direct APIs |

**Example with inference provider:**
```json
{
  "run_id": "run-9",
  "provider": "openai",
  "model": "whisper-large-v3",
  "inference_provider": "huggingface",
  "engine": "api",
  "run_method": {
    "interface": "api",
    "automation": "automated"
  }
}
```

## Run Notes Schema

The `run_notes` object provides structured metadata about the run configuration:

```json
{
  "run_notes": {
    "language_detection": {
      "auto_detect": boolean,
      "language_specified": boolean,
      "language_code": "string"
    },
    "model_params": {
      "temperature": number,
      "beam_size": number,
      "best_of": number
    },
    "formatting": {
      "punctuation": boolean,
      "smart_formatting": boolean,
      "diarization": boolean
    },
    "custom_annotations": {
      /* Flexible key-value pairs for additional notes */
    }
  }
}
```

### Language Detection Fields

| Field | Type | Description |
|-------|------|-------------|
| `auto_detect` | Boolean | If true, language was auto-detected; if false, language was specified |
| `language_specified` | Boolean | If true, a specific language was provided (same as !auto_detect) |
| `language_code` | String | The language code used ("en", "es", "auto", etc.) |

### Model Parameters Fields

| Field | Type | Description |
|-------|------|-------------|
| `temperature` | Number | Sampling temperature (0.0 = deterministic, higher = more random) |
| `beam_size` | Number | Beam search width |
| `best_of` | Number | Number of candidates to consider |

### Formatting Fields

| Field | Type | Description |
|-------|------|-------------|
| `punctuation` | Boolean | Whether automatic punctuation was enabled |
| `smart_formatting` | Boolean | Whether smart formatting (numbers, dates, etc.) was enabled |
| `diarization` | Boolean | Whether speaker diarization was enabled |

## Settings Object (Provider-Specific)

The `settings` object varies by provider. Common fields:

### Common Settings

```json
{
  "language": "en|auto-detect|es|fr|etc",
  "task": "transcribe|translate"
}
```

### OpenAI/Groq Whisper Settings

```json
{
  "language": "en",
  "temperature": 0.0,
  "prompt": "optional context string"
}
```

### Deepgram Settings

```json
{
  "language": "en",
  "smart_format": true,
  "punctuate": true,
  "diarize": false,
  "model": "nova-2"
}
```

### AssemblyAI Settings

```json
{
  "language_code": "en",
  "punctuate": true,
  "format_text": true,
  "speaker_labels": false
}
```

### Speechmatics Settings

```json
{
  "language": "en",
  "operating_point": "enhanced|standard",
  "enable_partials": false,
  "diarization": "none|speaker"
}
```

### Local (Buzz) Settings

```json
{
  "language": "en|auto-detect",
  "task": "transcribe",
  "model_size": "tiny|base|small|medium|large"
}
```

## Complete Example with All Fields

```json
{
  "run_id": "run-1",
  "run_type": "local-stt",
  "model": "whisper-base",
  "provider": "local",
  "inference_provider": null,
  "engine": "Buzz",
  "run_method": {
    "interface": "gui",
    "automation": "manual",
    "description": "Processed using Buzz desktop application"
  },
  "settings": {
    "language": "en",
    "task": "transcribe"
  },
  "output_dir": "runs/local-stt/run-1",
  "completed": true,
  "notes": "Whisper Base (local inference) using Buzz",
  "run_notes": {
    "language_detection": {
      "auto_detect": false,
      "language_specified": true,
      "language_code": "en"
    },
    "model_params": {
      "temperature": 0.0
    },
    "formatting": {
      "punctuation": true,
      "smart_formatting": false,
      "diarization": false
    },
    "custom_annotations": {
      "note": "First baseline run with English specified",
      "comparison_to": "run-3"
    }
  }
}
```

### Example: Cloud API Run

```json
{
  "run_id": "run-4",
  "run_type": "cloud-stt",
  "model": "whisper-1",
  "provider": "openai",
  "inference_provider": "direct",
  "engine": "api",
  "run_method": {
    "interface": "api",
    "automation": "automated",
    "description": "Executed via cloud_stt_runner.py script"
  },
  "settings": {
    "language": "en",
    "temperature": 0.0
  },
  "output_dir": "runs/cloud-stt/run-4",
  "completed": false,
  "notes": "OpenAI Whisper API",
  "run_notes": {
    "language_detection": {
      "auto_detect": false,
      "language_specified": true,
      "language_code": "en"
    }
  }
}
```

### Example: Via Inference Provider

```json
{
  "run_id": "run-9",
  "run_type": "cloud-stt",
  "model": "whisper-large-v3",
  "provider": "openai",
  "inference_provider": "huggingface",
  "engine": "api",
  "run_method": {
    "interface": "api",
    "automation": "automated",
    "description": "Via Hugging Face Inference API"
  },
  "settings": {
    "language": "en"
  },
  "output_dir": "runs/cloud-stt/run-9",
  "completed": false,
  "notes": "Whisper Large V3 via HuggingFace Inference API"
}
```

## Run Type Specific Fields

### Cloud STT Runs

Cloud runs typically use:
- `engine: "api"`
- Provider-specific API settings
- May include cost tracking in run_notes

### Local STT Runs

Local runs typically use:
- `engine: "Buzz"` or other local tools
- Simpler settings
- No API key requirements

### Manual Import Runs

Manual runs should include:
- `engine: "manual"`
- `completed: true`
- `metadata.manual_import: true` in metadata.json
- Custom provider name describing source

## Language Detection Strategy

Based on your note that "in all except one so far I provided English", here's how to annotate:

**English Specified (Most Runs):**
```json
"run_notes": {
  "language_detection": {
    "auto_detect": false,
    "language_specified": true,
    "language_code": "en"
  }
}
```

**Auto-Detect (run-3):**
```json
"run_notes": {
  "language_detection": {
    "auto_detect": true,
    "language_specified": false,
    "language_code": "auto"
  }
}
```

## Validation Rules

1. `run_id` must be unique across all runs
2. `output_dir` must be unique across all runs
3. `run_type` must be either "local-stt" or "cloud-stt"
4. `completed` must be boolean
5. If `run_notes.language_detection` exists:
   - `auto_detect` and `language_specified` should be opposites
   - `language_code` should match `settings.language` or `settings.language_code`

## Adding New Runs

When adding a new run:

1. Increment the run ID number
2. Choose appropriate `run_type`
3. Set `completed: false` initially
4. Add comprehensive `run_notes` for tracking configuration decisions
5. Ensure `output_dir` points to correct location
6. Set `completed: true` after successful transcription

## Migration Path

For existing runs without `run_notes`, you can add them incrementally:

1. Start with `language_detection` since this affects evaluation
2. Add `formatting` if those settings were used
3. Add `model_params` if non-default values were used
4. Use `custom_annotations` for any other important notes
