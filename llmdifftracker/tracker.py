import openai
import os
import glob
import difflib
from typing import Dict, Optional, Tuple


class LLMDiffTracker:
    def __init__(
        self,
        api_key: str,
        cache_dir: str = "./code_dump_cache",
        file_pattern: str = "*.py",
        system_prompt: str = "Summarize code changes. Be concise, and only include the most important changes. If it's too much, just return 'Too much code changes.'.",
        use_fal: bool = True,
    ):
        self.cache_dir = cache_dir
        self.file_pattern = file_pattern
        self.system_prompt = system_prompt
        self.use_fal = use_fal

        if use_fal:
            os.environ["FAL_KEY"] = api_key
            import fal_client

            self.fal_client = fal_client
        else:
            from openai import OpenAI

            self.openai_client = OpenAI(api_key=api_key)

        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "latest_dump.txt")

    def get_current_dump(self) -> str:
        file_contents = []
        for file in glob.glob(self.file_pattern, recursive=True):
            with open(file, "r", encoding="utf-8") as f:
                file_contents.append(f"# FILE: {file}\n" + f.read())
        return "\n".join(file_contents)

    def get_diff(self, old_text: str, new_text: str) -> str:
        diff = list(
            difflib.unified_diff(
                old_text.splitlines(), new_text.splitlines(), lineterm=""
            )
        )
        return "\n".join(diff)

    def summarize_diff(self, diff_text: str) -> str:
        if self.use_fal:

            def on_queue_update(update):
                if isinstance(update, self.fal_client.InProgress):
                    for log in update.logs:
                        print(log["message"])

            result = self.fal_client.subscribe(
                "fal-ai/any-llm",
                arguments={
                    "prompt": f"System: {self.system_prompt}\nUser: Summarize the following code changes: \n{diff_text}"
                },
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            return result["output"].strip()
        else:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"Summarize the following code changes: \n{diff_text}",
                    },
                ],
            )
            return response.choices[0].message.content.strip()

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

        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write(new_dump)

        if old_dump == "":
            print("No previous code dump found. Assuming first run.")
            return (
                "No previous code dump found. Assuming first run.",
                "No previous code dump found. Assuming first run.",
            )

        if not diff_text.strip():
            print("No code changes detected.")
            return "No code changes detected.", "No code changes detected."

        summary = self.summarize_diff(diff_text)

        return diff_text, summary


def patch_wandb():
    """Patches wandb.init to automatically track and log code changes."""
    try:
        import wandb
    except ImportError:
        raise ImportError(
            "wandb is required for this functionality. Install it with: pip install wandb"
        )

    original_wandb_init = wandb.init

    def patched_wandb_init(*args, **kwargs):
        run = original_wandb_init(*args, **kwargs)
        tracker = LLMDiffTracker(
            api_key=os.getenv("FAL_KEY", os.getenv("OPENAI_API_KEY")),
            use_fal="FAL_KEY" in os.environ,
        )
        result = tracker.track_changes()

        print(result)

        if result:
            diff_text, summary = result
            wandb.log({"diff_summary": summary, "diff_text": diff_text})

        return run

    wandb.init = patched_wandb_init
