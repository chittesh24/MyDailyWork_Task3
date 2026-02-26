"""
Evaluation metrics for image captioning.
Implements BLEU, METEOR, CIDEr, and ROUGE-L.
"""

import numpy as np
from typing import List, Dict
from collections import defaultdict

# Download required NLTK data
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from nltk.translate.bleu_score import corpus_bleu, sentence_bleu
from nltk.translate.meteor_score import meteor_score


class CaptionMetrics:
    """Compute multiple metrics for caption evaluation."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset stored predictions and references."""
        self.predictions = []
        self.references = []
    
    def update(self, predictions: List[str], references: List[List[str]]):
        """
        Add predictions and references.
        
        Args:
            predictions: List of predicted captions
            references: List of reference caption lists (multiple refs per image)
        """
        self.predictions.extend(predictions)
        self.references.extend(references)
    
    def compute_bleu(self, n: int = 4) -> Dict[str, float]:
        """
        Compute BLEU scores.
        
        Args:
            n: Maximum n-gram (4 for BLEU-1 to BLEU-4)
            
        Returns:
            scores: Dictionary with BLEU-1 to BLEU-n
        """
        # Tokenize
        tokenized_preds = [pred.split() for pred in self.predictions]
        tokenized_refs = [[ref.split() for ref in refs] for refs in self.references]
        
        scores = {}
        
        # BLEU-1 to BLEU-4
        for i in range(1, n + 1):
            weights = [1.0 / i] * i + [0] * (4 - i)
            score = corpus_bleu(
                tokenized_refs,
                tokenized_preds,
                weights=weights
            )
            scores[f'BLEU-{i}'] = score
        
        return scores
    
    def compute_meteor(self) -> float:
        """
        Compute METEOR score.
        
        Returns:
            score: Average METEOR score
        """
        scores = []
        
        for pred, refs in zip(self.predictions, self.references):
            # METEOR uses first reference by default
            score = meteor_score([refs[0].split()], pred.split())
            scores.append(score)
        
        return np.mean(scores)
    
    def compute_rouge_l(self) -> float:
        """
        Compute ROUGE-L score (F1 based on LCS).
        
        Returns:
            score: Average ROUGE-L F1
        """
        def lcs_length(x, y):
            """Compute longest common subsequence length."""
            m, n = len(x), len(y)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if x[i-1] == y[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            
            return dp[m][n]
        
        scores = []
        
        for pred, refs in zip(self.predictions, self.references):
            pred_tokens = pred.split()
            
            # Use best matching reference
            best_score = 0
            for ref in refs:
                ref_tokens = ref.split()
                
                lcs_len = lcs_length(pred_tokens, ref_tokens)
                
                if len(pred_tokens) == 0 or len(ref_tokens) == 0:
                    continue
                
                precision = lcs_len / len(pred_tokens) if len(pred_tokens) > 0 else 0
                recall = lcs_len / len(ref_tokens) if len(ref_tokens) > 0 else 0
                
                if precision + recall > 0:
                    f1 = 2 * precision * recall / (precision + recall)
                    best_score = max(best_score, f1)
            
            scores.append(best_score)
        
        return np.mean(scores)
    
    def compute_all(self) -> Dict[str, float]:
        """
        Compute all metrics.
        
        Returns:
            metrics: Dictionary with all scores
        """
        metrics = {}
        
        # BLEU
        bleu_scores = self.compute_bleu(n=4)
        metrics.update(bleu_scores)
        
        # METEOR
        metrics['METEOR'] = self.compute_meteor()
        
        # ROUGE-L
        metrics['ROUGE-L'] = self.compute_rouge_l()
        
        return metrics


def compute_metrics_for_batch(
    predictions: List[str],
    references: List[List[str]]
) -> Dict[str, float]:
    """
    Compute metrics for a batch of predictions.
    
    Args:
        predictions: List of predicted captions
        references: List of reference caption lists
        
    Returns:
        metrics: Dictionary of metric scores
    """
    evaluator = CaptionMetrics()
    evaluator.update(predictions, references)
    return evaluator.compute_all()
