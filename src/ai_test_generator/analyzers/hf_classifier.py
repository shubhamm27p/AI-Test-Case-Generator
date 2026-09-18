import logging
from typing import Dict, Any
from ..config import load_config

logger = logging.getLogger(__name__)

class HuggingFaceAnalyzer:
    """
    Optional NLP component utilizing Hugging Face for requirement analysis.
    Determines requirement quality, complexity, or categorizes the text.
    Gracefully falls back to heuristic analysis if HF is unavailable or offline.
    """
    def __init__(self, config=None):
        self.config = config or load_config()
        self.mode = self.config.mode
        self.classifier = None
        
        if self.mode != "mock" and self.config.huggingface_api_key:
            try:
                from transformers import pipeline
                # Initialize a lightweight HF pipeline
                # (Using zero-shot or basic text-classification as a proxy for requirement quality)
                self.classifier = pipeline("text-classification", model=self.config.huggingface_model)
            except Exception as e:
                logger.warning(f"Failed to load Hugging Face model: {e}. Falling back to heuristics.")

    def analyze_quality(self, requirement: str) -> Dict[str, Any]:
        """Analyzes the natural language requirement for quality and clarity."""
        if not requirement.strip():
            return {"score": 0.0, "status": "Empty requirement"}

        # Fallback / Mock behavior
        if self.mode == "mock" or not self.classifier:
            word_count = len(requirement.split())
            if word_count < 5:
                return {"score": 0.3, "status": "Poor (Too short, needs more detail)"}
            elif word_count > 100:
                return {"score": 0.7, "status": "Good (Detailed, but ensure it is not too complex)"}
            return {"score": 0.9, "status": "Excellent (Clear and concise)"}
        
        # Real HF inference
        try:
            # Truncate to avoid max length issues on small models
            result = self.classifier(requirement[:512])
            label = result[0]['label']
            score = result[0]['score']
            return {
                "score": score, 
                "status": f"Analyzed by HF ({label})"
            }
        except Exception as e:
            logger.error(f"HF analysis failed during inference: {e}")
            return {"score": 0.5, "status": "Analysis failed"}
