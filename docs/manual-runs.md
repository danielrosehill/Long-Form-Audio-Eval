# Manual Run Import Guide

If you run transcriptions manually (outside of the automated runner scripts), you can still include them in your evaluation by following this structure.

## Directory Structure

Manual runs should follow the same structure as automated runs:

```
runs/
├── cloud-stt/
│   └── run-X/
│       ├── transcript.txt       # Required: Plain text transcript
│       └── metadata.json        # Required: Run metadata
└── local-stt/
    └── run-X/
        ├── transcript.txt       # Required: Plain text transcript
        ├── transcript.srt       # Optional: SRT format
        └── metadata.json        # Required: Run metadata
```

## Steps to Import Manual Runs

### 1. Create Output Directory

Choose an unused run ID and create the directory:

```bash
mkdir -p runs/cloud-stt/run-9
# or
mkdir -p runs/local-stt/run-9
```

### 2. Add Your Transcript

Save your transcript as `transcript.txt`:

```bash
# Copy your transcript file
cp /path/to/your/transcript.txt runs/cloud-stt/run-9/transcript.txt
```

The transcript should be plain text with no special formatting.

### 3. Create Metadata File

Create `metadata.json` with the following structure:

```json
{
  "run_id": "run-9",
  "provider": "provider-name",
  "model": "model-name",
  "settings": {
    "language": "en"
  },
  "processing_time_seconds": 0,
  "timestamp": "2025-11-14 00:00:00",
  "audio_file": "data/audio/podcast.mp3",
  "output_file": "runs/cloud-stt/run-9/transcript.txt",
  "manual_import": true
}
```

**Fields:**
- `run_id`: Must match directory name
- `provider`: Service name (e.g., "rev", "otter", "custom")
- `model`: Model identifier
- `settings`: Any relevant settings (language, etc.)
- `processing_time_seconds`: Set to 0 if unknown
- `timestamp`: When transcription was created
- `audio_file`: Path to source audio
- `output_file`: Path to transcript file
- `manual_import`: Set to `true` to indicate manual import

### 4. Add to Configuration

Edit `config/runs-config.json` and add an entry:

```json
{
  "run_id": "run-9",
  "run_type": "cloud-stt",
  "model": "model-name",
  "provider": "provider-name",
  "engine": "manual",
  "settings": {
    "language": "en"
  },
  "output_dir": "runs/cloud-stt/run-9",
  "completed": true,
  "notes": "Manually imported transcript from [source]"
}
```

**Important:** Set `"completed": true` since the transcription is already done.

## Example: Importing a Rev.com Transcript

```bash
# 1. Create directory
mkdir -p runs/cloud-stt/run-9

# 2. Copy transcript
cp ~/Downloads/rev_transcript.txt runs/cloud-stt/run-9/transcript.txt

# 3. Create metadata
cat > runs/cloud-stt/run-9/metadata.json << 'EOF'
{
  "run_id": "run-9",
  "provider": "rev",
  "model": "human-transcription",
  "settings": {
    "language": "en",
    "verbatim": true
  },
  "processing_time_seconds": 0,
  "timestamp": "2025-11-14 12:30:00",
  "audio_file": "data/audio/podcast.mp3",
  "output_file": "runs/cloud-stt/run-9/transcript.txt",
  "manual_import": true
}
EOF

# 4. Edit config/runs-config.json and add:
# {
#   "run_id": "run-9",
#   "run_type": "cloud-stt",
#   "model": "human-transcription",
#   "provider": "rev",
#   "engine": "manual",
#   "settings": {
#     "language": "en",
#     "verbatim": true
#   },
#   "output_dir": "runs/cloud-stt/run-9",
#   "completed": true,
#   "notes": "Human transcription from Rev.com"
# }
```

## Validation

After importing, verify the structure:

```bash
# Check files exist
ls -la runs/cloud-stt/run-9/

# Verify transcript has content
wc -l runs/cloud-stt/run-9/transcript.txt

# Validate JSON
python -m json.tool runs/cloud-stt/run-9/metadata.json
```

## Using Manual Runs in Evaluation

Once properly imported, manual runs will be included in all evaluation scripts just like automated runs. The evaluation pipeline will:

1. Read the transcript from `transcript.txt`
2. Compare against ground truth using WER/CER metrics
3. Include results in comparison reports
4. Note `manual_import: true` in metadata for transparency

## Tips

- **Use consistent naming**: Choose descriptive provider names (e.g., "rev", "otter", "trint")
- **Document the source**: Use the `notes` field to explain where the transcript came from
- **Preserve original**: Keep a backup of the original transcript before any processing
- **Text format**: Ensure transcript is plain text (UTF-8) with no special formatting
- **Incremental IDs**: Use sequential run IDs to avoid conflicts
