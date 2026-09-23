"""
Root entry point for Streamlit Community Cloud and local execution.
"""
import sys
from pathlib import Path

# Add 'src' directory to Python path
src_path = str(Path(__file__).resolve().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ai_test_generator.ui.app import main

if __name__ == "__main__":
    main()
