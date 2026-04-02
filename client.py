"""
Client for connecting to the compliance audit environment.

Provides both synchronous and asynchronous methods for interacting with
the environment server via WebSocket.
"""

import asyncio
import json
from typing import Any

import websockets

from models import ComplianceAction, ComplianceObservation


class EnvClient:
    """
    Client for connecting to the compliance audit environment server via WebSocket.
    
    Provides both synchronous and asynchronous methods for interacting with the environment.
    Raises ConnectionError if the WebSocket connection is lost during operations.
    """
    
    def __init__(self, url: str = "ws://localhost:7860/ws"):
        """
        Initialize the environment client.
        
        Args:
            url: WebSocket URL of the environment server (default: ws://localhost:7860/ws)
        """
        self.url = url
        self._ws = None
        self._loop = None
    
    async def _connect(self) -> None:
        """Establish WebSocket connection to the server."""
        if self._ws is None or self._ws.closed:
            try:
                self._ws = await websockets.connect(self.url)
            except Exception as e:
                raise ConnectionError(f"Failed to connect to environment server at {self.url}: {e}")
    
    async def _send_and_receive(self, message: dict) -> dict:
        """
        Send a message to the server and receive the response.
        
        Args:
            message: Dictionary to send as JSON
            
        Returns:
            Response dictionary from the server
            
        Raises:
            ConnectionError: If WebSocket connection is lost
        """
        await self._connect()
        
        try:
            await self._ws.send(json.dumps(message))
            response = await self._ws.recv()
            return json.loads(response)
        except websockets.exceptions.ConnectionClosed as e:
            self._ws = None
            raise ConnectionError(f"WebSocket connection lost during operation: {e}")
        except Exception as e:
            raise ConnectionError(f"Communication error with environment server: {e}")
    
    async def async_reset(self, task: str) -> ComplianceObservation:
        """
        Asynchronously reset the environment with a new task.
        
        Args:
            task: Difficulty level - one of "easy", "medium", or "hard"
            
        Returns:
            Initial ComplianceObservation for the new episode
            
        Raises:
            ConnectionError: If WebSocket connection is lost
            ValueError: If task is invalid (raised by server)
        """
        message = {
            "type": "reset",
            "task": task
        }
        
        try:
            response = await self._send_and_receive(message)
            
            # Check for error response from server
            if "error" in response:
                raise ValueError(response["error"])
            
            # Parse observation from response
            return ComplianceObservation(**response["observation"])
        except ConnectionError:
            raise
        except Exception as e:
            raise ConnectionError(f"Failed to reset environment: {e}")
    
    async def async_step(
        self, 
        action: ComplianceAction
    ) -> tuple[ComplianceObservation, float, bool, dict]:
        """
        Asynchronously execute one step in the environment.
        
        Args:
            action: ComplianceAction containing violation_ids, explanation, and suggested_rewrite
            
        Returns:
            Tuple of (observation, reward, done, info)
            
        Raises:
            ConnectionError: If WebSocket connection is lost
            RuntimeError: If step called before reset (raised by server)
        """
        message = {
            "type": "step",
            "action": action.model_dump()
        }
        
        try:
            response = await self._send_and_receive(message)
            
            # Check for error response from server
            if "error" in response:
                raise RuntimeError(response["error"])
            
            # Parse response components
            observation = ComplianceObservation(**response["observation"])
            reward = float(response["reward"])
            done = bool(response["done"])
            info = dict(response.get("info", {}))
            
            return observation, reward, done, info
        except ConnectionError:
            raise
        except Exception as e:
            raise ConnectionError(f"Failed to execute step: {e}")
    
    def reset(self, task: str) -> ComplianceObservation:
        """
        Synchronously reset the environment with a new task.
        
        Args:
            task: Difficulty level - one of "easy", "medium", or "hard"
            
        Returns:
            Initial ComplianceObservation for the new episode
            
        Raises:
            ConnectionError: If WebSocket connection is lost
            ValueError: If task is invalid
        """
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        
        try:
            return self._loop.run_until_complete(self.async_reset(task))
        except ConnectionError as e:
            raise ConnectionError(f"WebSocket connection lost during reset: {e}")
    
    def step(
        self, 
        action: ComplianceAction
    ) -> tuple[ComplianceObservation, float, bool, dict]:
        """
        Synchronously execute one step in the environment.
        
        Args:
            action: ComplianceAction containing violation_ids, explanation, and suggested_rewrite
            
        Returns:
            Tuple of (observation, reward, done, info)
            
        Raises:
            ConnectionError: If WebSocket connection is lost
            RuntimeError: If step called before reset
        """
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        
        try:
            return self._loop.run_until_complete(self.async_step(action))
        except ConnectionError as e:
            raise ConnectionError(f"WebSocket connection lost during step: {e}")
    
    async def async_close(self) -> None:
        """Asynchronously close the WebSocket connection."""
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()
            self._ws = None
    
    def close(self) -> None:
        """Synchronously close the WebSocket connection."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        
        self._loop.run_until_complete(self.async_close())
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close connection."""
        await self.async_close()
