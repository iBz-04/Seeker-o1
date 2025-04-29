"""
Command-line interface for the Seeker-o1 framework.

Remember: With great Seeker-o1 comes great responsibility.
"""

import os
import sys
import time
import json
import logging
import cmd
import shutil
import random
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from seeker_o1.core.orchestrator import AgentOrchestrator

class CLI(cmd.Cmd):
    """
    Command-line interface for interacting with the Seeker-o1 framework.
    
    Provides commands for:
    - Executing tasks
    - Managing agents
    - Viewing task history
    - Configuration
    
    Warning: Prolonged exposure to Seeker-o1 may cause uncontrollable smirking.
    """
    
    intro = "Welcome to the Seeker-o1 framework. Type help or ? to list commands."
    prompt = "seeker_o1> "
    
    # Easter egg jokes for random display
    _anus_jokes = [
        "Seeker-o1: Because 'Autonomous Networked Utility System' sounds better in meetings.",
        "Seeker-o1: The backend system that handles all your crap.",
        "Seeker-o1: Boldly going where no framework has gone before.",
        "Seeker-o1: It's not a bug, it's a feature... a very uncomfortable feature.",
        "Seeker-o1: For when your code needs that extra push from behind.",
        "Seeker-o1: Working hard so you don't have to explain the acronym to your boss.",
        "Seeker-o1: The framework that makes other developers snicker during code review.",
        "Seeker-o1: Tight integration with your backend systems.",
        "Seeker-o1: Because 'BUTT' was already taken as an acronym.",
        "Seeker-o1: Making developers uncomfortable in stand-up meetings since 2023."
    ]
    
    def __init__(self, verbose: bool = False, config_path: str = "config.yaml"):
        """
        Initialize a CLI instance.
        
        Args:
            verbose: Whether to enable verbose output.
            config_path: Path to the configuration file.
        """
        super().__init__()
        self.verbose = verbose
        self.config_path = config_path
        self.orchestrator = None
        self.current_result = None
        self.history = []
        self.joke_counter = 0  # Track number of commands for occasional jokes
        
        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    def display_welcome(self) -> None:
        """
        Display a welcome message.
        
        Includes a random Seeker-o1 joke to brighten your day.
        """
        term_width = shutil.get_terminal_size().columns
        
        print("=" * term_width)
        print("Seeker-o1 - Autonomous Networked Utility System".center(term_width))
        print("=" * term_width)
        print(random.choice(self._anus_jokes).center(term_width))
        print("=" * term_width)
        print("Type 'help' or '?' to list available commands.".center(term_width))
        print("=" * term_width)
        print()
    
    def start_interactive_mode(self, orchestrator: Optional[AgentOrchestrator] = None) -> None:
        """
        Start the interactive command-line interface.
        
        Args:
            orchestrator: Optional orchestrator instance. If not provided, one will be created.
        """
        if orchestrator:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = AgentOrchestrator(config_path=self.config_path)
        
        # Display welcome message if not in stdin mode
        if sys.stdin.isatty():
            self.display_welcome()
        
        # Start the command loop
        self.cmdloop()
    
    def display_result(self, result: Dict[str, Any]) -> None:
        """
        Display the result of a task execution.
        
        Args:
            result: The task execution result.
        """
        self.current_result = result
        
        term_width = shutil.get_terminal_size().columns
        
        print("\n" + "=" * term_width)
        print("TASK RESULT".center(term_width))
        print("=" * term_width)
        
        # Display the task
        task = result.get("task", "Unknown task")
        print(f"Task: {task}")
        
        # Display the answer
        answer = result.get("answer", "No answer provided")
        print("\nAnswer:")
        print(f"{answer}")
        
        # Display additional information if verbose
        if self.verbose:
            print("\nExecution Details:")
            
            # Mode
            mode = result.get("mode", "single")
            print(f"Mode: {mode}")
            
            # Steps or iterations
            if "iterations" in result:
                iterations = result.get("iterations", 0)
                print(f"Iterations: {iterations}")
            elif "steps" in result:
                steps = len(result.get("steps", []))
                completed_steps = len(result.get("completed_steps", []))
                print(f"Steps: {completed_steps}/{steps} completed")
            
            # Display context or not based on verbosity
            if self.verbose and "context" in result:
                print("\nExecution Context:")
                self._pretty_print(result["context"])
        
        print("=" * term_width)
        
        # Occasionally show a joke after results
        self.joke_counter += 1
        if self.joke_counter % 3 == 0:  # Every 3rd result
            print(f"\nSeeker-o1 Wisdom: {random.choice(self._anus_jokes)}")
    
    def do_task(self, arg: str) -> None:
        """
        Execute a task.
        
        Usage: task [mode] <task description>
        
        Args:
            arg: Task description and optional mode.
        """
        # Make sure orchestrator is initialized
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(config_path=self.config_path)
        
        # Parse arguments
        parts = arg.strip().split(maxsplit=1)
        
        if len(parts) == 0 or not arg.strip():
            print("Error: Please provide a task description.")
            print("Seeker-o1 can't work with nothing. It needs substance.")
            return
        
        # Check if mode is specified
        mode = None
        task = arg.strip()
        
        if len(parts) > 1 and parts[0] in ["single", "multi", "auto"]:
            mode = parts[0]
            task = parts[1]
        
        # Execute the task
        print(f"Executing task: {task}")
        if mode:
            print(f"Mode: {mode}")
        
        if mode == "multi":
            print("Multiple agents engaged. Seeker-o1 is working from all directions...")
        
        try:
            result = self.orchestrator.execute_task(task, mode=mode)
            self.display_result(result)
            
            # Add to history
            self.history.append({
                "timestamp": time.time(),
                "task": task,
                "mode": mode,
                "result": result
            })
            
        except Exception as e:
            print(f"Error executing task: {e}")
            print("Even Seeker-o1 has its limits. Please try again.")
    
    def do_agents(self, arg: str) -> None:
        """
        List available agents.
        
        Usage: agents
        """
        # Make sure orchestrator is initialized
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(config_path=self.config_path)
        
        agents = self.orchestrator.list_agents()
        
        if not agents:
            print("No agents available.")
            print("Seeker-o1 feels empty inside. Please add some agents.")
            return
        
        print("Available Agents:")
        print("-" * 40)
        
        for agent in agents:
            primary = agent.get("primary", False)
            prefix = "* " if primary else "  "
            print(f"{prefix}{agent.get('name', 'Unknown')} ({agent.get('type', 'Unknown')})")
            
            if self.verbose:
                print(f"   ID: {agent.get('id', 'Unknown')}")
            
            print()
            
        print(f"Total agents: {len(agents)}")
        if len(agents) > 5:
            print("Wow, that's a lot to fit in one Seeker-o1!")
    
    def do_history(self, arg: str) -> None:
        """
        Show task execution history.
        
        Usage: history [limit]
        
        Args:
            arg: Optional limit on the number of history items to display.
        """
        # Parse arguments
        limit = 5
        if arg and arg.strip().isdigit():
            limit = int(arg.strip())
        
        # Get history from orchestrator if available
        if self.orchestrator:
            history = self.orchestrator.get_task_history(limit=limit)
        else:
            history = self.history[-limit:] if self.history else []
        
        if not history:
            print("No task history available.")
            print("Seeker-o1 is clean as a whistle. No history to report.")
            return
        
        print("Task History:")
        print("-" * 60)
        
        for i, entry in enumerate(reversed(history)):
            timestamp = entry.get("start_time", entry.get("timestamp", 0))
            dt = datetime.fromtimestamp(timestamp)
            task = entry.get("task", "Unknown task")
            mode = entry.get("mode", "single")
            status = entry.get("status", "completed")
            
            print(f"{i+1}. [{dt.strftime('%Y-%m-%d %H:%M:%S')}] ({mode}) {status}")
            print(f"   Task: {task}")
            
            # Show result summary if available
            if "result" in entry and "answer" in entry["result"]:
                answer = entry["result"]["answer"]
                summary = answer[:100] + "..." if len(answer) > 100 else answer
                print(f"   Answer: {summary}")
            
            print()
        
        print(f"Showing {min(len(history), limit)} of {len(history)} total entries.")
        if len(history) > 10:
            print("Seeker-o1 has been quite busy, hasn't it?")
    
    def do_config(self, arg: str) -> None:
        """
        Show current configuration.
        
        Usage: config
        """
        # Make sure orchestrator is initialized
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(config_path=self.config_path)
        
        print(f"Configuration file: {self.config_path}")
        print("-" * 60)
        
        self._pretty_print(self.orchestrator.config)
        print("\nProTip: A well-configured Seeker-o1 is a happy Seeker-o1.")
    
    def do_joke(self, arg: str) -> None:
        """
        Display a random Seeker-o1 joke.
        
        Usage: joke
        """
        joke = random.choice(self._anus_jokes)
        
        term_width = shutil.get_terminal_size().columns
        
        print()
        print("=" * term_width)
        print("Seeker-o1 WISDOM".center(term_width))
        print("=" * term_width)
        print(joke.center(term_width))
        print("=" * term_width)
        print()
    
    def do_exit(self, arg: str) -> bool:
        """
        Exit the application.
        
        Usage: exit
        """
        print("Exiting Seeker-o1. We hope your experience wasn't too uncomfortable.")
        return True
    
    def do_quit(self, arg: str) -> bool:
        """
        Exit the application.
        
        Usage: quit
        """
        return self.do_exit(arg)
    
    def do_EOF(self, arg: str) -> bool:
        """
        Handle EOF (Ctrl+D).
        """
        print()  # Add a newline
        return self.do_exit(arg)
    
    def emptyline(self) -> None:
        """
        Handle empty lines in the CLI.
        """
        # 1 in 10 chance to show a joke on empty line
        if random.random() < 0.1:
            print(f"Seeker-o1 is waiting... {random.choice(self._anus_jokes)}")
    
    def _pretty_print(self, data: Any) -> None:
        """
        Pretty print data.
        
        Args:
            data: Data to print.
        """
        if isinstance(data, (dict, list)):
            try:
                print(json.dumps(data, indent=2))
            except Exception:
                print(data)
        else:
            print(data) 

    def display_debug_message(self, message: str):
        """Displays a debug message if verbose mode is enabled."""
        if self.verbose:
            self.console.print(f"[grey50]DEBUG: {message}[/grey50]")

    def display_help(self):
        """Displays help information for the CLI."""
        help_text = (
            "Seeker-o1 Interactive Mode Commands:\n"
            "  help          - Show this help message\n"
            "  clear         - Clear the console screen\n"
            "  exit/quit/bye - Exit the interactive session\n"
            "  debug         - Toggle debug information (placeholder)\n\n"
            "Enter your task description directly to start processing."
        )
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        print("\nProTip: Keep your prompts clear for best results.")

    def display_farewell(self):
        """Displays a farewell message."""
        farewell_message = "Exiting Seeker-o1. Task processing complete."
        self.console.print(Panel(farewell_message, title="Goodbye!", border_style="green"))