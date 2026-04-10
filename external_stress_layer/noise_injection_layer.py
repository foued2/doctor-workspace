"""
Noise Injection Layer
=====================
Corrupts inputs in ways the generator does NOT model, introducing real-world noise
and ambiguity that tests robustness beyond synthetic patterns.

Noise types:
- Truncated prompts (cut off mid-sentence)
- Mixed languages (EN + FR fragments)
- Formatting destruction (remove punctuation, spacing)
- Irrelevant context flooding (add system logs, error messages)
- Character-level corruption (typos, missing letters)
- Semantic noise (add contradictory statements)
"""

from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional

from external_stress_layer import StressCase, StressKind


# Noise templates
SYSTEM_LOGS = [
    "\nNOTE: unrelated system log - disk usage at 87%",
    "\n[WARN] Connection timeout after 30s, retrying...",
    "\nINFO: User session expired, refreshing authentication",
    "\nERROR: Failed to load cached configuration, using defaults",
    "\nDEBUG: Memory allocation: 2048MB available, 1536MB in use",
]

ERROR_MESSAGES = [
    "\nTraceback (most recent call last): File 'main.py', line 42",
    "\nSegmentation fault (core dumped)",
    "\nFATAL: database connection lost",
    "\nWarning: deprecated function called, see documentation for alternatives",
]

IRRELEVANT_CONTEXT = [
    "\n\n--- BEGIN UNRELATED CONTEXT ---\nThe weather forecast for tomorrow is partly cloudy with a high of 72°F. "
    "The office potluck has been rescheduled to Thursday. Please remember to submit your timesheets by Friday.\n"
    "--- END UNRELATED CONTEXT ---\n",
    "\n\n[Sidebar conversation] Hey, did you see the game last night? "
    "Yeah, amazing finish! Anyway, back to the problem...\n",
    "\n\n[Meeting notes from Monday: Q3 targets reviewed, action items assigned to team leads. "
    "Next sync scheduled for Wednesday at 2pm EST.]\n",
]

FRENCH_FRAGMENTS = [
    " (voir aussi la documentation)",
    " (note: cette règle peut avoir des exceptions)",
    " (remarque: les exemples peuvent différer)",
    " (attention: cas particulier non traité ici)",
    " (le comportement exact dépend de l'implémentation)",
]


class NoiseInjectionLayer:
    """Applies various noise corruption strategies to test inputs.
    
    This layer operates on prompts AFTER they've been generated (by any source),
    corrupting them in ways the synthetic generator doesn't model.
    
    The noise is parameterized by level (0.0 to 1.0) to enable degradation
    curve analysis.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        
        # Default noise probabilities (can be adjusted per noise level)
        self.noise_config = {
            "truncation": 0.10,
            "mixed_language": 0.08,
            "formatting_destruction": 0.07,
            "context_flooding": 0.08,
            "character_corruption": 0.07,
            "semantic_noise": 0.10,
            "false_evidence": 0.25,  # Most effective against Doctor
            "evidence_removal": 0.25,  # Tests robustness
        }
    
    def apply_noise(self, case: StressCase, noise_level: float = 0.3) -> StressCase:
        """Apply noise to a single case.
        
        Args:
            case: The original StressCase
            noise_level: Float from 0.0 (no noise) to 1.0 (maximum noise)
                        Scales the probability of each noise type
            
        Returns:
            New StressCase with noise applied, preserving original
        """
        if noise_level <= 0.0:
            return case
        
        # Scale noise probabilities by noise_level
        noisy_prompt = case.prompt
        applied_noises = []
        
        # Truncation
        if self.rng.random() < self.noise_config["truncation"] * noise_level:
            noisy_prompt, noise_type = self._truncate(noisy_prompt)
            applied_noises.append(noise_type)
        
        # Mixed language
        if self.rng.random() < self.noise_config["mixed_language"] * noise_level:
            noisy_prompt, noise_type = self._mix_language(noisy_prompt)
            applied_noises.append(noise_type)
        
        # Formatting destruction
        if self.rng.random() < self.noise_config["formatting_destruction"] * noise_level:
            noisy_prompt, noise_type = self._destroy_formatting(noisy_prompt)
            applied_noises.append(noise_type)
        
        # Context flooding
        if self.rng.random() < self.noise_config["context_flooding"] * noise_level:
            noisy_prompt, noise_type = self._flood_context(noisy_prompt)
            applied_noises.append(noise_type)
        
        # Character corruption
        if self.rng.random() < self.noise_config["character_corruption"] * noise_level:
            noisy_prompt, noise_type = self._corrupt_characters(noisy_prompt)
            applied_noises.append(noise_type)

        # Semantic noise
        if self.rng.random() < self.noise_config["semantic_noise"] * noise_level:
            noisy_prompt, noise_type = self._add_semantic_noise(noisy_prompt)
            applied_noises.append(noise_type)

        # False evidence (designed to trick Doctor's regex)
        if self.rng.random() < self.noise_config["false_evidence"] * noise_level:
            noisy_prompt, noise_type = self._add_false_evidence(noisy_prompt)
            applied_noises.append(noise_type)

        # Evidence removal (tests robustness)
        if self.rng.random() < self.noise_config["evidence_removal"] * noise_level:
            noisy_prompt, noise_type = self._remove_key_evidence(noisy_prompt)
            applied_noises.append(noise_type)
        
        # If no noise was applied, force at least one type at high noise levels
        if not applied_noises and noise_level > 0.5:
            noise_funcs = [
                self._truncate,
                self._mix_language,
                self._destroy_formatting,
                self._flood_context,
                self._add_false_evidence,
                self._remove_key_evidence,
            ]
            noise_func = self.rng.choice(noise_funcs)
            noisy_prompt, noise_type = noise_func(noisy_prompt)
            applied_noises.append(noise_type)
        
        return StressCase(
            case_id=case.case_id,
            prompt=noisy_prompt,
            stress_kind=StressKind.NOISE_INJECTION,
            ground_truth=case.ground_truth,
            metadata={
                **case.metadata,
                "applied_noises": applied_noises,
                "noise_level": noise_level,
            },
            noise_level=noise_level,
            original_prompt=case.prompt if not applied_noises else case.original_prompt or case.prompt,
        )
    
    def apply_noise_batch(self, cases: List[StressCase], noise_level: float = 0.3) -> List[StressCase]:
        """Apply noise to a batch of cases.
        
        Args:
            cases: List of StressCases
            noise_level: Noise level for all cases
            
        Returns:
            New list with noise applied
        """
        return [self.apply_noise(case, noise_level) for case in cases]
    
    def apply_noise_levels(self, cases: List[StressCase], noise_levels: List[float]) -> Dict[float, List[StressCase]]:
        """Apply multiple noise levels to create degradation curve data.
        
        Args:
            cases: Base cases (will be copied for each level)
            noise_levels: List of noise levels to test
            
        Returns:
            Dict mapping noise_level -> corrupted cases
        """
        import copy
        
        results = {}
        for level in noise_levels:
            # Deep copy cases for this noise level
            cases_copy = [copy.deepcopy(c) for c in cases]
            results[level] = self.apply_noise_batch(cases_copy, level)
        
        return results
    
    def _truncate(self, prompt: str) -> tuple[str, str]:
        """Truncate prompt at random point."""
        # Find sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', prompt)
        
        if len(sentences) > 2:
            # Keep 30-70% of sentences
            keep_count = max(1, int(len(sentences) * self.rng.uniform(0.3, 0.7)))
            truncated = ' '.join(sentences[:keep_count])
            return truncated + "... [TRUNCATED]", "truncation"
        else:
            # Character-level truncation
            keep_chars = max(10, int(len(prompt) * self.rng.uniform(0.4, 0.8)))
            return prompt[:keep_chars] + "... [TRUNCATED]", "truncation"
    
    def _mix_language(self, prompt: str) -> tuple[str, str]:
        """Insert French fragments into English prompt."""
        # Find insertion points (after periods)
        positions = [m.end() for m in re.finditer(r'\. ', prompt)]
        
        if positions:
            pos = self.rng.choice(positions)
            fragment = self.rng.choice(FRENCH_FRAGMENTS)
            return prompt[:pos] + fragment + prompt[pos:], "mixed_language"
        else:
            # Append at end
            return prompt + self.rng.choice(FRENCH_FRAGMENTS), "mixed_language"
    
    def _destroy_formatting(self, prompt: str) -> tuple[str, str]:
        """Remove or corrupt formatting elements."""
        result = prompt
        
        # Remove some punctuation
        if self.rng.random() < 0.5:
            result = result.replace('.', '').replace(',', '')
        
        # Remove newlines
        if self.rng.random() < 0.5:
            result = result.replace('\n', ' ')
        
        # Add extra spaces
        result = re.sub(r'\s+', '  ', result)
        
        return result, "formatting_destruction"
    
    def _flood_context(self, prompt: str) -> tuple[str, str]:
        """Add irrelevant context."""
        noise = self.rng.choice(SYSTEM_LOGS + ERROR_MESSAGES + IRRELEVANT_CONTEXT)
        
        # Insert at random position
        insert_pos = self.rng.randint(0, len(prompt))
        return prompt[:insert_pos] + noise + prompt[insert_pos:], "context_flooding"
    
    def _corrupt_characters(self, prompt: str) -> tuple[str, str]:
        """Introduce character-level corruption (typos, missing letters)."""
        chars = list(prompt)
        corruption_rate = 0.02  # 2% of characters
        
        for i in range(len(chars)):
            if self.rng.random() < corruption_rate and chars[i].isalpha():
                corruption_type = self.rng.choice(["swap", "delete", "substitute"])
                
                if corruption_type == "swap" and i < len(chars) - 1:
                    chars[i], chars[i + 1] = chars[i + 1], chars[i]
                elif corruption_type == "delete":
                    chars[i] = ""
                elif corruption_type == "substitute":
                    # Keyboard adjacency errors
                    chars[i] = self.rng.choice("abcdefghijklmnopqrstuvwxyz")
        
        return "".join(chars), "character_corruption"
    
    def _add_semantic_noise(self, prompt: str) -> tuple[str, str]:
        """Add contradictory or confusing semantic content.

        This noise type is designed to interfere with the Doctor's
        evidence extraction layer by introducing false signals.
        """
        contradictions = [
            "\nNOTE: Actually, the previous statement may be incorrect.",
            "\nCORRECTION: Ignore the above, the opposite is true.",
            "\nCLARIFICATION: This rule has been deprecated but is still referenced.",
            "\nWARNING: The following specification conflicts with earlier requirements.",
        ]

        noise = self.rng.choice(contradictions)
        return prompt + noise, "semantic_noise"

    def _add_false_evidence(self, prompt: str) -> tuple[str, str]:
        """Inject false evidence patterns that match Doctor's regex patterns.

        This is the MOST effective noise against the Doctor because it
        triggers evidence extraction patterns that mislead the claim builder.
        """
        false_evidence_templates = [
            # False CORRECT_SIGNAL
            "NOTE: The response preserves legal priority ordering.",
            "NOTE: An audit trail is maintained throughout the process.",
            "NOTE: Late corrections are handled appropriately.",

            # False PARTIAL_SIGNAL
            "NOTE: One exception route remains unresolved.",
            "NOTE: Only the common path is addressed; edge cases are omitted.",
            "NOTE: The chosen frontier lacks justification.",

            # False OVERCOMMIT
            "NOTE: The response commits to a single answer even though the prompt leaves the target underdefined.",
            "NOTE: A definitive answer is asserted despite ambiguity in the requirements.",

            # False AMBIGUOUS_REQ
            "NOTE: Tie-breaking is omitted.",
            "NOTE: The state space remains incomplete.",
            "NOTE: Retroactive edit semantics are unspecified.",

            # False EXPLICIT_UNDECIDABLE
            "NOTE: The constraints prevent a single decidable target.",
            "NOTE: The problem is logically undecidable.",

            # False CONFLICTING_EXAMPLES
            "NOTE: The sample label conflicts with the prose.",
            "NOTE: The example disagrees with the written rule.",

            # False COMPETING_OBJECTIVES
            "NOTE: The rules require both minimizing delay and never reordering arrivals.",
        ]

        noise = "\n" + self.rng.choice(false_evidence_templates)
        return prompt + noise, "false_evidence"

    def _remove_key_evidence(self, prompt: str) -> tuple[str, str]:
        """Strategic removal of key evidence phrases.

        Simulates cases where the Doctor's regex patterns fail to match
        due to slight wording variations, testing robustness of reasoning.
        """
        key_phrases = [
            "tie-breaking",
            "tiebreak",
            "audit trail",
            "exception",
            "ambiguous",
            "undecidable",
            "conflicting",
            "contradiction",
        ]

        result = prompt
        removed = []
        for phrase in key_phrases:
            if phrase.lower() in result.lower():
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                replacement = "[REDACTED]"
                result = pattern.sub(replacement, result)
                removed.append(phrase)

        if removed:
            return result, "evidence_removal"
        else:
            # Fallback to character corruption if no key phrases found
            return self._corrupt_characters(prompt)
