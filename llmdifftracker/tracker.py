import openai
import os
import glob
import difflib
from typing import Dict, Optional, Tuple

class LLMDiffTracker:
    def __init__(self, openai_api_key: str, cache_dir: str = "./code_dump_cache", 
                 file_pattern: str = "*.py", system_prompt: str = "Summarize code changes"):
        self.cache_dir = cache_dir
        self.file_pattern = file_pattern
        self.system_prompt = system_prompt
        openai.api_key = openai_api_key
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "latest_dump.txt")

    def get_current_dump(self) -> str:
        file_contents = []
        for file in glob.glob(self.file_pattern, recursive=True):
            with open(file, "r", encoding="utf-8") as f:
                file_contents.append(f"# FILE: {file}\n" + f.read())
        return "\n".join(file_contents)

    def get_diff(self, old_text: str, new_text: str) -> str:
        diff = list(difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm=""))
        return "\n".join(diff)

    def summarize_diff(self, diff_text: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Summarize the following code changes: \n{diff_text}"}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()

    def track_changes(self) -> Optional[Tuple[str, str]]:
        """Track code changes and return diff text and summary.
        
        Returns:
            Optional[Tuple[str, str]]: A tuple of (diff_text, summary) if changes detected,
                                     None if no changes detected.
        """
        new_dump = self.get_current_dump()
        old_dump = ""
        
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                old_dump = f.read()
        
        diff_text = self.get_diff(old_dump, new_dump)
        
        if not diff_text.strip():
            print("No code changes detected.")
            return None
        
        summary = self.summarize_diff(diff_text)
        
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write(new_dump)
        
        return diff_text, summary

def patch_wandb():
    """Patches wandb.init to automatically track and log code changes."""
    try:
        import wandb
    except ImportError:
        raise ImportError("wandb is required for this functionality. Install it with: pip install wandb")

    original_wandb_init = wandb.init
    
    def patched_wandb_init(*args, **kwargs):
        run = original_wandb_init(*args, **kwargs)
        tracker = LLMDiffTracker(openai_api_key=os.getenv("OPENAI_API_KEY"))
        result = tracker.track_changes()
        
        if result:
            diff_text, summary = result
            wandb.log({
                "diff_summary": summary,
                "diff_text": diff_text
            })
        
        return run
    
    wandb.init = patched_wandb_init 