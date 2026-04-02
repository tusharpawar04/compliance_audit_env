"""
Inference Script for Compliance Audit Environment
==================================================

MANDATORY REQUIREMENTS:
- Uses OpenAI Client with API_BASE_URL, MODEL_NAME, HF_TOKEN from environment
- Emits structured stdout logs in [START], [STEP], [END] format
- Must be named `inference.py` and placed in root directory
- Runtime < 20 minutes
- Works on vcpu=2, memory=8gb

ENVIRONMENT VARIABLES:
- API_BASE_URL: The API endpoint for the LLM (default: https://router.huggingface.co/v1)
- MODEL_NAME: The model identifier (default: Qwen/Qwen2.5-72B-Instruct)
- HF_TOKEN: Your Hugging Face API key
- TASK_NAME: Task difficulty (default: easy)
"""

import json
import os
import random
import sys
from typing import List, Optional

from openai import OpenAI

from client import EnvClient
from models import ComplianceAction, ComplianceObservation

# Environment configuration
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("TASK_NAME", "easy")
BENCHMARK = "compliance-audit-env"
SPACE_URL = os.getenv("SPACE_URL", "https://tusharpawar21-compliance-audit-env.hf.space")

# Episode configuration
MAX_STEPS = 3  # Environment allows up to 3 attempts
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Success threshold
SUCCESS_SCORE_THRESHOLD = 0.85  # Environment ends at 0.85 score


def log_start(task: str, env: str, model: str) -> None:
    """Emit [START] log line."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int, action: str, reward: float, done: bool, error: Optional[str]
) -> None:
    """Emit [STEP] log line."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Truncate action for logging if too long
    action_str = action[:100] + "..." if len(action) > 100 else action
    print(
        f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Emit [END] log line."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def create_prompt(observation: ComplianceObservation) -> str:
    """
    Create a prompt for the LLM based on the current observation.
    
    Args:
        observation: Current ComplianceObservation from the environment
        
    Returns:
        Formatted prompt string for the model
    """
    system_prompt = """You are an expert regulatory compliance officer specializing in GDPR audits.
Your task is to identify violations in company privacy policies and data processing agreements."""

    user_prompt = f"""Company: {observation.company_name}
Document ID: {observation.doc_id}
Task Difficulty: {observation.task_name}
Current Step: {observation.step_num}

Document to Audit:
{observation.document_text}

GDPR Rules Reference:
{json.dumps(observation.rules_reference, indent=2) if isinstance(observation.rules_reference, dict) else observation.rules_reference}
"""

    if observation.feedback:
        user_prompt += f"\n\nPrevious Feedback: {observation.feedback}"
        user_prompt += f"\nPrevious Score: {observation.previous_score:.2f}"

    user_prompt += """

Your task:
1. Identify ALL GDPR rule violations in the document (provide rule IDs like RULE_01, RULE_02, etc.)
2. Explain your legal reasoning for each violation
3. For hard tasks: Suggest a compliant rewrite that addresses all violations

Respond in JSON format with:
{
  "violation_ids": ["RULE_XX", "RULE_YY"],
  "explanation": "Your detailed legal reasoning",
  "suggested_rewrite": "Your compliant rewrite (or empty string for easy/medium tasks)"
}
"""

    return system_prompt, user_prompt


def get_model_action(
    client: OpenAI, observation: ComplianceObservation
) -> ComplianceAction:
    """
    Get an action from the LLM for the current observation.
    
    Args:
        client: OpenAI API client
        observation: Current observation from environment
        
    Returns:
        ComplianceAction to take
    """
    system_prompt, user_prompt = create_prompt(observation)

    try:
        # Use structured output with Pydantic model
        response = client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ComplianceAction,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        action = response.choices[0].message.parsed

        if action is None:
            # Fallback if parsing fails
            return ComplianceAction(
                violation_ids=[],
                explanation="API parsing failed",
                suggested_rewrite="",
            )

        return action

    except Exception as e:
        print(f"[DEBUG] Model request failed: {e}", file=sys.stderr, flush=True)
        # Return empty action on error
        return ComplianceAction(
            violation_ids=[], explanation=f"Error: {str(e)}", suggested_rewrite=""
        )


def main() -> None:
    """
    Main inference function.
    
    Runs one episode of the compliance audit environment with the specified task.
    Emits structured logs in [START], [STEP], [END] format.
    """
    # Set random seed for reproducibility
    random.seed(42)

    # Validate API key
    if not API_KEY:
        print("[ERROR] HF_TOKEN or API_KEY environment variable not set", flush=True)
        log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
        log_end(success=False, steps=0, score=0.0, rewards=[])
        sys.exit(1)

    # Initialize OpenAI client
    try:
        openai_client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}", flush=True)
        log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
        log_end(success=False, steps=0, score=0.0, rewards=[])
        sys.exit(1)

    # Initialize environment client
    # Convert HTTPS URL to WSS for WebSocket connection
    env_url = SPACE_URL.replace("https://", "wss://").replace("http://", "ws://") + "/ws"
    
    # Allow override for local testing
    env_url = os.getenv("ENV_URL", env_url)

    try:
        client = EnvClient(url=env_url)
    except Exception as e:
        print(f"[ERROR] Failed to connect to environment: {e}", flush=True)
        log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
        log_end(success=False, steps=0, score=0.0, rewards=[])
        sys.exit(1)

    # Episode tracking
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    # Emit [START] log
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset environment
        observation = client.reset(TASK_NAME)
        done = False

        # Run episode
        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            # Get action from model
            action = get_model_action(openai_client, observation)

            # Create action string for logging
            action_str = f"violations={action.violation_ids}"

            # Execute step
            try:
                observation, reward, done, info = client.step(action)
                error = None
            except Exception as e:
                print(f"[DEBUG] Step execution failed: {e}", file=sys.stderr, flush=True)
                error = str(e)
                reward = 0.0
                done = True

            # Track metrics
            rewards.append(reward)
            steps_taken = step
            score = reward  # Last reward is the score

            # Emit [STEP] log
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

            if done:
                break

        # Determine success
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[ERROR] Episode failed: {e}", file=sys.stderr, flush=True)
        success = False

    finally:
        # Close client
        try:
            client.close()
        except Exception as e:
            print(
                f"[DEBUG] Client close error: {e}", file=sys.stderr, flush=True
            )

        # Emit [END] log (always emitted)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
