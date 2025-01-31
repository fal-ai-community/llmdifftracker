# llmdifftracker

A Python package that tracks and summarizes code changes using OpenAI's GPT. This tool helps you maintain better documentation of your code changes during development by automatically generating summaries of code modifications. It can be used standalone or integrated with Weights & Biases for experiment tracking.

## Features

- Automatic code change detection
- LLM-powered change summarization using OpenAI's GPT
- Optional integration with Weights & Biases for experiment tracking
- Easy to use with a simple API

## Installation

### Basic Installation
```bash
pip install git+https://github.com/cloneofsimo/llmdifftracker.git
```

### Installation with Weights & Biases Support
```bash
pip install "git+https://github.com/cloneofsimo/llmdifftracker.git#egg=llmdifftracker[wandb]"
```

## Usage

### Basic Usage (Standalone)

```python
from llmdifftracker import LLMDiffTracker
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Initialize the tracker
tracker = LLMDiffTracker(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    cache_dir="./code_dump_cache",  # Where to store code snapshots
    file_pattern="*.py",  # Which files to track
    system_prompt="Summarize code changes"  # Custom prompt for GPT
)

# Track changes
result = tracker.track_changes()
if result:
    diff_text, summary = result
    print("Code changes detected!")
    print("Summary:", summary)
    print("Diff:", diff_text)
```

### Integration with Weights & Biases

```python
import wandb
from llmdifftracker import patch_wandb
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Patch wandb.init to automatically track code changes
patch_wandb()

# Now, every time you call wandb.init(), code changes will be tracked
wandb.init(project="your-project-name")
```

## How it Works

1. The package takes a snapshot of your code files
2. When changes are detected, it generates a diff
3. The diff is sent to OpenAI's GPT for summarization
4. The diff and summary are returned (and optionally logged to Weights & Biases)

## Requirements

- Python 3.6+
- OpenAI API key
- (Optional) Weights & Biases account

## License

MIT License

## Author

Simo Ryu (cloneofsimo)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 