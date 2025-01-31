"""
llmdifftracker - A package for tracking and summarizing code changes using LLMs
"""

from .tracker import LLMDiffTracker, patch_wandb

__version__ = "0.1.0"
__author__ = "Simo Ryu (cloneofsimo)"

__all__ = ["LLMDiffTracker", "patch_wandb"] 