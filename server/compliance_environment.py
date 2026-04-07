"""
Core environment logic for compliance auditing.

This is where episodes are managed, actions are graded, and feedback is generated.
Agents connect to this environment via the FastAPI server and interact through
reset() and step() calls.
"""

import random
from dataclasses import dataclass
from typing import Any

from openenv.core.env_server import Environment

from models import ComplianceAction, ComplianceObservation
from server.compliance_data import DOCUMENTS, RULES, RULE_CATEGORIES


@dataclass
class EpisodeState:
    """Internal state tracking for the current episode."""
    document: dict
    task_name: str
    step_num: int
    previous_score: float
    feedback: str


class ComplianceEnvironment(Environment):
    """
    Reinforcement learning environment for regulatory compliance auditing.
    
    Agents act as compliance officers, identifying GDPR violations in company documents
    and suggesting compliant rewrites. The environment provides three difficulty levels
    (easy, medium, hard) with corresponding grading strategies.
    """
    
    def __init__(self):
        """Initialize the environment with no active episode."""
        super().__init__()
        self._episode_state: EpisodeState | None = None
    
    def reset(self, task: str = "easy") -> ComplianceObservation:
        """
        Reset the environment and start a new episode.
        
        Args:
            task: Difficulty level - must be one of "easy", "medium", or "hard"
            
        Returns:
            Initial ComplianceObservation with step_num=1, empty feedback, and score=0.0
            
        Raises:
            ValueError: If task is not one of the valid difficulty levels
        """
        valid_tasks = ["easy", "medium", "hard"]
        if task not in valid_tasks:
            raise ValueError(f"Invalid task: {task}. Must be one of {', '.join(valid_tasks)}")
        
        # Select a random document matching the difficulty
        matching_docs = [doc for doc in DOCUMENTS if doc["difficulty"] == task]
        document = random.choice(matching_docs)
        
        # Initialize episode state with step_num=1
        self._episode_state = EpisodeState(
            document=document,
            task_name=task,
            step_num=1,
            previous_score=0.0,
            feedback=""
        )
        
        # Return initial observation
        return ComplianceObservation(
            doc_id=document["doc_id"],
            company_name=document["company_name"],
            document_text=document["document_text"],
            rules_reference=RULES,
            task_name=task,
            step_num=1,
            feedback="",
            previous_score=0.0,
            reward=0.0,
            done=False
        )

    def _grade_easy(self, action: ComplianceAction) -> float:
        """
        Easy grader using F1 score for violation detection.
        
        Computes precision and recall comparing predicted vs actual violation IDs,
        then returns the harmonic mean (F1 score).
        
        Args:
            action: Agent's compliance action
            
        Returns:
            F1 score in range (0.0, 1.0) - strictly between 0 and 1
        """
        predicted = set(action.violation_ids)
        actual = set(self._episode_state.document["violation_ids"])
        
        # Handle edge cases - return small non-zero value instead of 0.0
        if len(predicted) == 0:
            return 0.001
        if len(actual) == 0:
            return 0.001
        
        # Compute precision and recall
        intersection = predicted & actual
        precision = len(intersection) / len(predicted)
        recall = len(intersection) / len(actual)
        
        # Compute F1 score
        if precision + recall == 0:
            return 0.001
        
        f1 = 2 * precision * recall / (precision + recall)
        
        # Clamp to strictly between 0 and 1
        return max(0.001, min(0.999, f1))
    
    def _grade_medium(self, action: ComplianceAction) -> float:
        """
        Medium grader with exact match + category partial credit.
        
        For each known violation:
        - Full credit (1.0 / len(actual)) if exact rule ID match
        - Partial credit (0.5 / len(actual)) if category match but different rule ID
        - Zero credit otherwise
        
        Args:
            action: Agent's compliance action
            
        Returns:
            Score in range (0.0, 1.0) - strictly between 0 and 1
        """
        actual = self._episode_state.document["violation_ids"]
        predicted = action.violation_ids
        
        if len(actual) == 0:
            return 0.001
        
        total_credit = 0.0
        
        for known_violation in actual:
            if known_violation in predicted:
                # Exact match - full credit
                total_credit += 1.0 / len(actual)
            else:
                # Check for category match
                known_category = RULE_CATEGORIES.get(known_violation)
                if known_category:
                    for predicted_rule in predicted:
                        predicted_category = RULE_CATEGORIES.get(predicted_rule)
                        if predicted_category == known_category:
                            # Category match - partial credit at 0.5 weight
                            total_credit += 0.5 / len(actual)
                            break  # Only award partial credit once per known violation
        
        # Clamp to strictly between 0 and 1
        return max(0.001, min(0.999, total_credit))
    
    def _grade_hard(self, action: ComplianceAction) -> float:
        """
        Hard grader combining detection score and rewrite quality.
        
        Composite score: 60% detection (using medium grader) + 40% rewrite quality.
        Rewrite quality is measured by keyword coverage in the suggested rewrite.
        
        Args:
            action: Agent's compliance action
            
        Returns:
            Composite score in range (0.0, 1.0) - strictly between 0 and 1
        """
        # Use medium grader for detection score (partial category credit)
        detection_score = self._grade_medium(action)
        
        # Compute rewrite quality score
        rewrite_keywords = self._episode_state.document.get("rewrite_keywords", [])
        
        if len(rewrite_keywords) == 0:
            rewrite_score = 0.001
        else:
            suggested_rewrite_lower = action.suggested_rewrite.lower()
            keyword_hits = sum(
                1 for keyword in rewrite_keywords 
                if keyword.lower() in suggested_rewrite_lower
            )
            rewrite_score = keyword_hits / len(rewrite_keywords)
        
        # Composite: 60% detection + 40% rewrite
        composite_score = 0.6 * detection_score + 0.4 * rewrite_score
        
        # Clamp to strictly between 0 and 1
        return max(0.001, min(0.999, composite_score))

    def step(self, action: ComplianceAction) -> ComplianceObservation:
        """
        Execute one step in the environment with the agent's action.
        
        Grades the action based on the current task difficulty, updates episode state,
        and determines if the episode is done (step_num >= 3 or score >= 0.85).
        
        Args:
            action: Agent's compliance action
            
        Returns:
            ComplianceObservation with updated state, reward, and done flag
            
        Raises:
            RuntimeError: If no active episode (reset not called)
        """
        if self._episode_state is None:
            raise RuntimeError("No active episode. Call reset() first.")
        
        # Dispatch to appropriate grader based on task difficulty
        if self._episode_state.task_name == "easy":
            score = self._grade_easy(action)
        elif self._episode_state.task_name == "medium":
            score = self._grade_medium(action)
        elif self._episode_state.task_name == "hard":
            score = self._grade_hard(action)
        else:
            raise ValueError(f"Unknown task: {self._episode_state.task_name}")
        
        # Generate feedback
        feedback = f"Score: {score:.2f}"
        
        # Increment step number
        self._episode_state.step_num += 1
        
        # Determine if episode is done
        done = self._episode_state.step_num >= 3 or score >= 0.85
        
        # Create observation with reward and done embedded
        observation = ComplianceObservation(
            doc_id=self._episode_state.document["doc_id"],
            company_name=self._episode_state.document["company_name"],
            document_text=self._episode_state.document["document_text"],
            rules_reference=RULES,
            task_name=self._episode_state.task_name,
            step_num=self._episode_state.step_num,
            feedback=feedback,
            previous_score=score,
            reward=score,
            done=done
        )
        
        # Update episode state
        self._episode_state.previous_score = score
        self._episode_state.feedback = feedback
        
        return observation
    
    def state(self) -> dict:
        """
        Return a snapshot of the current episode state.
        
        Returns:
            Dict containing doc_id, task_name, step_num, and previous_score
        """
        if self._episode_state is None:
            return {
                "doc_id": None,
                "task_name": None,
                "step_num": 0,
                "previous_score": 0.0
            }
        
        return {
            "doc_id": self._episode_state.document["doc_id"],
            "task_name": self._episode_state.task_name,
            "step_num": self._episode_state.step_num,
            "previous_score": self._episode_state.previous_score
        }
