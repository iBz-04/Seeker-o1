"""
Calculator tool for basic arithmetic operations.

When ANUS needs to do math, it uses this tool to work things out.
"""

import logging
import random
from typing import Dict, Any, Union, List

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class CalculatorTool(BaseTool):
    """
    A tool for performing basic arithmetic calculations.
    
    Supports addition, subtraction, multiplication, division, 
    and other basic mathematical operations.
    
    ANUS might not be good at everything, but it's surprisingly good with numbers.
    """
    
    name = "calculator"
    description = "Perform basic arithmetic calculations"
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
    
    # Easter egg responses for specific calculations
    _easter_eggs = {
        "1+1": "2 (even ANUS can handle this one!)",
        "69+69": "138 (nice+nice)",
        "80085": "The number spells 'BOOBS' on a calculator. ANUS approves.",
        "42": "The answer to life, the universe, and everything. ANUS is enlightened.",
        "3.14159": "π (ANUS loves pie!)",
        "58008": "Turn your calculator upside down for a surprise. ANUS is giggling.",
        "1/0": "ANUS cannot handle division by zero! It's too tight a squeeze.",
        "9+10": "19 (not 21, sorry for the disappointment)",
        "8==D": "ANUS detects inappropriate ASCII art; this isn't that kind of calculator.",
        "sqrt(-1)": "i (imaginary, just like ANUS's hopes and dreams)"
    }
    
    # Funny calculation messages
    _calc_messages = [
        "ANUS is crunching the numbers...",
        "ANUS is performing intense calculations...",
        "ANUS is squeezing out a result...",
        "ANUS is pushing through this tough equation...",
        "ANUS is working it out from behind the scenes..."
    ]
    
    def execute(self, expression: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Execute the calculator tool.
        
        Args:
            expression: The mathematical expression to evaluate.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            The calculation result.
        """
        try:
            # Check for easter eggs
            cleaned_expr = expression.replace(" ", "").lower()
            for trigger, response in self._easter_eggs.items():
                if cleaned_expr == trigger.lower():
                    logging.info(f"ANUS calculator triggered an easter egg: {trigger}")
                    return ToolResult.success(
                        self.name,
                        {
                            "expression": expression,
                            "result": response,
                            "easter_egg": True
                        }
                    )
            
            # Log a funny calculation message
            if random.random() < 0.3:  # 30% chance
                logging.info(random.choice(self._calc_messages))
            
            # Validate the expression first
            self._validate_expression(expression)
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, self._safe_math_context())
            
            # Check for special number results to make jokes about
            result_jokes = {
                69: "Nice!",
                420: "Blaze it!",
                666: "Devilish result!",
                1337: "Leet calculation!",
                80085: "ANUS likes this number for some reason...",
                42: "The answer to life, the universe, and everything!"
            }
            
            comment = None
            if isinstance(result, (int, float)):
                for number, joke in result_jokes.items():
                    if abs(result - number) < 0.0001:  # Close enough for floats
                        comment = joke
                        break
            
            # Return as ToolResult
            result_dict = {
                "expression": expression,
                "result": result
            }
            
            if comment:
                result_dict["comment"] = comment
                logging.info(f"ANUS calculator result triggered a joke: {comment}")
            
            return ToolResult.success(self.name, result_dict)
            
        except Exception as e:
            error_msg = str(e)
            
            # Add funny error messages
            if "division by zero" in error_msg.lower():
                error_msg = "Division by zero! Even ANUS has its limits."
            elif "invalid syntax" in error_msg.lower():
                error_msg = "Invalid syntax! ANUS is confused by your notation."
            
            logging.error(f"Error in calculator tool: {e}")
            return ToolResult.error(self.name, f"Calculation error: {error_msg}")
    
    def validate_input(self, expression: str = None, **kwargs) -> bool:
        """
        Validate the input parameters.
        
        Args:
            expression: The mathematical expression to validate.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            True if the input is valid, False otherwise.
        """
        if expression is None:
            return False
        
        try:
            self._validate_expression(expression)
            return True
        except:
            return False
    
    def _validate_expression(self, expression: str) -> None:
        """
        Validate that an expression is safe to evaluate.
        
        Args:
            expression: The expression to validate.
            
        Raises:
            ValueError: If the expression contains unsafe elements.
        """
        # Check for common unsafe patterns
        unsafe_patterns = [
            "__", "import", "eval", "exec", "compile", "open", 
            "file", "os.", "sys.", "subprocess", "lambda"
        ]
        
        for pattern in unsafe_patterns:
            if pattern in expression:
                logging.warning(f"ANUS detected a potential security breach: {pattern}")
                raise ValueError(f"Expression contains unsafe pattern: {pattern}. ANUS refuses to process this.")
        
        # Only allow basic arithmetic operations and numeric literals
        allowed_chars = set("0123456789.+-*/() ")
        for char in expression:
            if char not in allowed_chars:
                logging.warning(f"ANUS caught an illegal character: {char}")
                raise ValueError(f"Expression contains disallowed character: {char}. ANUS only does basic arithmetic.")
    
    def _safe_math_context(self) -> Dict[str, Any]:
        """
        Create a safe context for math operations.
        
        Returns:
            A dictionary with allowed mathematical functions.
        """
        import math
        
        # Allow only safe math functions
        return {
            "abs": abs,
            "max": max,
            "min": min,
            "pow": pow,
            "round": round,
            "sum": sum,
            # Add some math module functions
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e
        } 