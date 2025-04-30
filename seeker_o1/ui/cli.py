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
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich import box
from rich.style import Style

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
    _seeker_o1_jokes = [
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
        self.console = Console()
        
        # Set styled prompt
        self.raw_prompt = "seeker_o1> "
        self.prompt = self.raw_prompt  # Keep plain prompt for cmd module
    
    def display_welcome(self) -> None:
        """
        Display a welcome message.
        
        Includes a random Seeker-o1 joke to brighten your day.
        """
        term_width = shutil.get_terminal_size().columns
        
        # Create a title panel
        title = Text("Seeker-o1", style="bold cyan")
        subtitle = Text("Autonomous Networked Utility System", style="italic")
        version = Text("v1.0.0", style="dim")
        
        # Create a joke text
        joke_text = random.choice(self._seeker_o1_jokes)
        
        # Create centered content
        content = "\n".join([
            f"[bold cyan]{' ' * ((term_width - len('Seeker-o1')) // 2)}Seeker-o1[/bold cyan]",
            f"[italic]{' ' * ((term_width - len('Autonomous Networked Utility System')) // 2)}Autonomous Networked Utility System[/italic]",
            f"[dim]{' ' * ((term_width - len('v1.0.0')) // 2)}v1.0.0[/dim]",
            "",
            f"[yellow italic]{' ' * ((term_width - len(joke_text)) // 2)}{joke_text}[/yellow italic]"
        ])
        
        # Combine into panel
        welcome_panel = Panel(
            content,
            border_style="cyan",
            box=box.ROUNDED,
            title="Welcome to Seeker-o1",
            subtitle="Type 'help' or '?' to list available commands"
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
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
        
        # Display the task
        task = result.get("task", "Unknown task")
        
        # Display the answer
        answer = result.get("answer", "No answer provided")
        
        # Create a result panel
        result_panel = Panel(
            f"[bold cyan]Task:[/bold cyan] {task}\n\n[bold green]Answer:[/bold green]\n{answer}",
            border_style="green",
            box=box.ROUNDED,
            title="Task Result",
            subtitle="Seeker-o1 Execution"
        )
        
        self.console.print(result_panel)
        
        # Display additional information if verbose
        if self.verbose:
            details = []
            
            # Mode
            mode = result.get("mode", "single")
            details.append(f"[bold]Mode:[/bold] {mode}")
            
            # Steps or iterations
            if "iterations" in result:
                iterations = result.get("iterations", 0)
                details.append(f"[bold]Iterations:[/bold] {iterations}")
            elif "steps" in result:
                steps = len(result.get("steps", []))
                completed_steps = len(result.get("completed_steps", []))
                details.append(f"[bold]Steps:[/bold] {completed_steps}/{steps} completed")
            
            details_panel = Panel(
                "\n".join(details),
                border_style="blue",
                box=box.ROUNDED,
                title="Execution Details"
            )
            
            self.console.print(details_panel)
            
            # Display context or not based on verbosity
            if self.verbose and "context" in result:
                self.console.print("[bold]Execution Context:[/bold]")
                self._pretty_print(result["context"])
        
        # Occasionally show a joke after results
        self.joke_counter += 1
        if self.joke_counter % 3 == 0:  # Every 3rd result
            self.console.print(f"\n[italic yellow]Seeker-o1 Wisdom:[/italic yellow] {random.choice(self._seeker_o1_jokes)}")
    
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
            self.console.print("[bold red]Error:[/bold red] Please provide a task description.")
            self.console.print("[italic]Seeker-o1 can't work with nothing. It needs substance.[/italic]")
            return
        
        # Check if mode is specified
        mode = None
        task = arg.strip()
        
        if len(parts) > 1 and parts[0] in ["single", "multi", "auto"]:
            mode = parts[0]
            task = parts[1]
        
        # Show task info
        self.console.print(f"[bold cyan]Executing task:[/bold cyan] {task}")
        if mode:
            self.console.print(f"[bold cyan]Mode:[/bold cyan] {mode}")
        
        if mode == "multi":
            self.console.print("[italic]Multiple agents engaged. Seeker-o1 is working from all directions...[/italic]")
        
        # Execute the task with progress indicator
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]Processing...[/bold cyan]"),
                BarColumn(),
                TextColumn("[bold]{task.description}[/bold]"),
                TimeElapsedColumn()
            ) as progress:
                task_id = progress.add_task("Executing task", total=None)
                
                # Use a separate thread for execution to show progress
                result = self.orchestrator.execute_task(task, mode=mode)
                progress.update(task_id, completed=100)
            
            self.display_result(result)
            
            # Add to history
            self.history.append({
                "timestamp": time.time(),
                "task": task,
                "mode": mode,
                "result": result
            })
            
        except Exception as e:
            self.console.print(f"[bold red]Error executing task:[/bold red] {e}")
            self.console.print("[italic]Even Seeker-o1 has its limits. Please try again.[/italic]")
    
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
            self.console.print("[bold yellow]No agents available.[/bold yellow]")
            self.console.print("[italic]Seeker-o1 feels empty inside. Please add some agents.[/italic]")
            return
        
        # Create a table for agents
        table = Table(title="Available Agents", box=box.ROUNDED)
        table.add_column("", style="cyan", no_wrap=True)
        table.add_column("Name", style="bold white")
        table.add_column("Type", style="green")
        if self.verbose:
            table.add_column("ID", style="dim")
        
        for agent in agents:
            primary = agent.get("primary", False)
            prefix = "✓" if primary else " "
            
            row = [
                prefix,
                agent.get("name", "Unknown"),
                agent.get("type", "Unknown")
            ]
            
            if self.verbose:
                row.append(agent.get("id", "Unknown"))
                
            table.add_row(*row)
        
        self.console.print(table)
        self.console.print(f"Total agents: {len(agents)}")
        if len(agents) > 5:
            self.console.print("[italic]Wow, that's a lot to fit in one Seeker-o1![/italic]")
    
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
            self.console.print("[bold yellow]No task history available.[/bold yellow]")
            self.console.print("[italic]Seeker-o1 is clean as a whistle. No history to report.[/italic]")
            return
        
        # Create a table for history
        table = Table(title="Task History", box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Mode", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Task", style="bold white")
        
        for i, entry in enumerate(reversed(history)):
            timestamp = entry.get("start_time", entry.get("timestamp", 0))
            dt = datetime.fromtimestamp(timestamp)
            task = entry.get("task", "Unknown task")
            mode = entry.get("mode", "single")
            status = entry.get("status", "completed")
            
            table.add_row(
                str(i+1),
                dt.strftime("%Y-%m-%d %H:%M:%S"),
                mode,
                status,
                task[:50] + "..." if len(task) > 50 else task
            )
        
        self.console.print(table)
        
        # Show result details if requested
        if len(history) > 0 and self.verbose:
            latest = history[-1]
            if "result" in latest and "answer" in latest["result"]:
                answer = latest["result"]["answer"]
                
                answer_panel = Panel(
                    answer,
                    title="Latest Result",
                    border_style="green"
                )
                self.console.print(answer_panel)
        
        self.console.print(f"Showing {min(len(history), limit)} of {len(history)} total entries.")
        if len(history) > 10:
            self.console.print("[italic]Seeker-o1 has been quite busy, hasn't it?[/italic]")
    
    def do_config(self, arg: str) -> None:
        """
        Show current configuration.
        
        Usage: config
        """
        # Make sure orchestrator is initialized
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(config_path=self.config_path)
        
        self.console.print(f"[bold cyan]Configuration file:[/bold cyan] {self.config_path}")
        
        # Display config as syntax highlighted JSON
        try:
            config_json = json.dumps(self.orchestrator.config, indent=2)
            syntax = Syntax(config_json, "json", theme="monokai", line_numbers=True)
            self.console.print(Panel(
                syntax,
                title="Configuration",
                border_style="blue",
                box=box.ROUNDED
            ))
            self.console.print("\n[italic]ProTip: A well-configured Seeker-o1 is a happy Seeker-o1.[/italic]")
        except Exception:
            # Fallback to regular pretty print if something goes wrong
            self._pretty_print(self.orchestrator.config)
    
    def do_joke(self, arg: str) -> None:
        """
        Display a random Seeker-o1 joke.
        
        Usage: joke
        """
        joke = random.choice(self._seeker_o1_jokes)
        
        joke_panel = Panel(
            joke,
            title="Seeker-o1 WISDOM",
            border_style="yellow",
            box=box.ROUNDED
        )
        
        self.console.print()
        self.console.print(joke_panel)
        self.console.print()
    
    def do_exit(self, arg: str) -> bool:
        """
        Exit the application.
        
        Usage: exit
        """
        self.display_farewell()
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
        self.console.print()  # Add a newline
        return self.do_exit(arg)
    
    def emptyline(self) -> None:
        """
        Handle empty lines in the CLI.
        """
        # 1 in 10 chance to show a joke on empty line
        if random.random() < 0.1:
            self.console.print(f"[dim italic]Seeker-o1 is waiting... {random.choice(self._seeker_o1_jokes)}[/dim italic]")
    
    def _pretty_print(self, data: Any) -> None:
        """
        Pretty print data.
        
        Args:
            data: Data to print.
        """
        if isinstance(data, (dict, list)):
            try:
                # Use rich for pretty printing
                self.console.print_json(json.dumps(data))
            except Exception:
                self.console.print(data)
        else:
            self.console.print(data) 

    def display_debug_message(self, message: str):
        """Displays a debug message if verbose mode is enabled."""
        if self.verbose:
            self.console.print(f"[grey50]DEBUG: {message}[/grey50]")

    def display_help(self):
        """Displays help information for the CLI."""
        # Create a table for commands
        table = Table(title="Seeker-o1 Commands", box=box.ROUNDED)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Usage", style="green")
        
        # Add rows for each command
        table.add_row("task", "Execute a task", "task [mode] <description>")
        table.add_row("agents", "List available agents", "agents")
        table.add_row("history", "Show task execution history", "history [limit]")
        table.add_row("config", "Show current configuration", "config")
        table.add_row("joke", "Display a random joke", "joke")
        table.add_row("exit/quit", "Exit the application", "exit")
        table.add_row("help/?", "Show this help message", "help")
        
        self.console.print(table)
        self.console.print("\n[italic]ProTip: Keep your prompts clear for best results.[/italic]")

    def display_farewell(self):
        """Displays a farewell message."""
        farewell_panel = Panel(
            "Thank you for using Seeker-o1!\nExiting now...",
            title="Goodbye!",
            border_style="green",
            box=box.ROUNDED
        )
        self.console.print(farewell_panel)

    def cmdloop(self, intro=None):
        """Override cmdloop to handle Rich styling for prompt"""
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.console.print(self.intro)
            
        stop = None
        while not stop:
            try:
                # Print styled prompt
                self.console.print("[bold cyan]seeker_o1[/bold cyan][bold white]>[/bold white] ", end="")
                line = input()
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            except KeyboardInterrupt:
                self.console.print("^C")
            except EOFError:
                self.console.print()
                stop = self.do_EOF("")