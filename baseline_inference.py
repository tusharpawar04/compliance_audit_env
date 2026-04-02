"""
Baseline performance test using GPT-4o-mini.

Runs the environment with GPT-4o-mini to establish reference scores.
This is optional - the environment works fine without it.

Expected scores:
- Easy: ~0.70
- Medium: ~0.43
- Hard: ~0.22

Usage:
    export OPENAI_API_KEY="your-key-here"
    python baseline_inference.py
"""

import json
import logging
import os
import random
from typing import Any

from openai import OpenAI

from client import EnvClient
from models import ComplianceAction, ComplianceObservation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_prompt(observation: ComplianceObservation) -> str:
    """
    Create a prompt for the GPT-4o-mini model based on the current observation.
    
    Args:
        observation: Current ComplianceObservation from the environment
        
    Returns:
        Formatted prompt string for the model
    """
    prompt = f"""You are a regulatory compliance officer auditing company documents for GDPR violations.

Company: {observation.company_name}
Document ID: {observation.doc_id}
Task Difficulty: {observation.task_name}
Current Step: {observation.step_num}

Document to Audit:
{observation.document_text}

GDPR Rules Reference:
{observation.rules_reference}

"""
    
    if observation.feedback:
        prompt += f"\nPrevious Feedback: {observation.feedback}\n"
        prompt += f"Previous Score: {observation.previous_score:.2f}\n"
    
    prompt += """
Your task:
1. Identify all GDPR rule violations in the document (provide rule IDs like RULE_01, RULE_02, etc.)
2. Explain your legal reasoning for each violation
3. Suggest a compliant rewrite of the document that addresses all violations

Respond with:
- violation_ids: List of rule IDs that are violated
- explanation: Your legal reasoning explaining the violations
- suggested_rewrite: Your proposed compliant version of the document
"""
    
    return prompt


def run_episode(
    client: EnvClient,
    openai_client: OpenAI,
    task: str,
    episode_num: int
) -> float:
    """
    Run a single episode for the given task difficulty.
    
    Args:
        client: EnvClient connected to the environment server
        openai_client: OpenAI API client
        task: Task difficulty level ("easy", "medium", or "hard")
        episode_num: Episode number for logging
        
    Returns:
        Final reward/score for the episode
        
    Raises:
        Exception: If episode fails critically
    """
    logger.info(f"Starting episode {episode_num + 1} for task '{task}'")
    
    try:
        # Reset environment
        observation = client.reset(task)
        done = False
        final_reward = 0.0
        step_count = 0
        
        while not done:
            step_count += 1
            logger.info(f"  Step {step_count} - Generating action with GPT-4o-mini...")
            
            # Create prompt from observation
            prompt = create_prompt(observation)
            
            try:
                # Call OpenAI API with structured output
                response = openai_client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert regulatory compliance officer specializing in GDPR audits."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format=ComplianceAction,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Extract the structured action
                action = response.choices[0].message.parsed
                
                if action is None:
                    logger.error(f"  OpenAI API returned None for parsed action")
                    # Create a fallback empty action
                    action = ComplianceAction(
                        violation_ids=[],
                        explanation="API parsing failed",
                        suggested_rewrite=""
                    )
                
                logger.info(f"  Action generated: {len(action.violation_ids)} violations identified")
                
            except Exception as e:
                logger.error(f"  OpenAI API error: {e}")
                # Create a fallback empty action to continue the episode
                action = ComplianceAction(
                    violation_ids=[],
                    explanation=f"Error: {str(e)}",
                    suggested_rewrite=""
                )
            
            # Execute step in environment
            observation, reward, done, info = client.step(action)
            final_reward = reward
            
            logger.info(f"  Step {step_count} completed - Reward: {reward:.4f}, Done: {done}")
        
        logger.info(f"Episode {episode_num + 1} completed - Final score: {final_reward:.4f}")
        return final_reward
        
    except Exception as e:
        logger.error(f"Episode {episode_num + 1} failed: {e}")
        raise


def main():
    """
    Main function to run baseline inference across all tasks.
    
    Runs 3 episodes per task for each of ["easy", "medium", "hard"],
    computes mean scores, and outputs JSON results.
    """
    # Set random seed for reproducibility
    random.seed(42)
    logger.info("Random seed set to 42 for reproducibility")
    
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        print(json.dumps({"error": "OPENAI_API_KEY not set"}))
        return
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized")
    
    # Initialize environment client
    env_url = os.environ.get("ENV_URL", "ws://localhost:7860/ws")
    logger.info(f"Connecting to environment at {env_url}")
    
    try:
        client = EnvClient(url=env_url)
    except Exception as e:
        logger.error(f"Failed to create EnvClient: {e}")
        print(json.dumps({"error": f"Failed to connect to environment: {str(e)}"}))
        return
    
    # Run episodes for each task
    tasks = ["easy", "medium", "hard"]
    results: dict[str, float] = {}
    
    for task in tasks:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running task: {task.upper()}")
        logger.info(f"{'='*60}")
        
        scores = []
        
        for episode_num in range(3):
            try:
                score = run_episode(client, openai_client, task, episode_num)
                scores.append(score)
            except Exception as e:
                logger.error(f"Skipping episode {episode_num + 1} due to error: {e}")
                # Continue with remaining episodes
                continue
        
        # Compute mean score for this task
        if scores:
            mean_score = sum(scores) / len(scores)
            results[task] = mean_score
            logger.info(f"\nTask '{task}' completed - Mean score: {mean_score:.4f} (from {len(scores)} episodes)")
        else:
            logger.error(f"No successful episodes for task '{task}'")
            results[task] = 0.0
    
    # Close client connection
    try:
        client.close()
    except Exception as e:
        logger.warning(f"Error closing client: {e}")
    
    # Output results as JSON
    logger.info(f"\n{'='*60}")
    logger.info("FINAL RESULTS")
    logger.info(f"{'='*60}")
    print(json.dumps(results, indent=2))
    
    # Log comparison with expected baseline
    logger.info("\nComparison with expected baseline:")
    expected = {"easy": 0.70, "medium": 0.43, "hard": 0.22}
    for task in tasks:
        if task in results:
            diff = results[task] - expected[task]
            logger.info(f"  {task}: {results[task]:.4f} (expected: {expected[task]:.4f}, diff: {diff:+.4f})")


if __name__ == "__main__":
    main()
