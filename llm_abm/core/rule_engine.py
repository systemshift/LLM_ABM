"""
Rule engine for LLM-generated custom rules

Provides safe execution environment for dynamically created rules while maintaining
the functional programming approach of the library.
"""
import copy
import ast
import inspect
from typing import Dict, Any, Callable

class SafeRuleValidator:
    """Validates LLM-generated rule code for safety"""
    
    # Allowed built-in functions
    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
        'float', 'int', 'len', 'list', 'map', 'max', 'min', 'range',
        'round', 'set', 'sorted', 'str', 'sum', 'tuple', 'zip'
    }
    
    # Allowed imports (library modules only)
    ALLOWED_IMPORTS = {
        'copy': ['deepcopy', 'copy'],
        'random': ['random', 'choice', 'randint', 'uniform'],
        'math': ['sqrt', 'sin', 'cos', 'pi', 'exp', 'log']
    }
    
    # Forbidden AST node types (Import/ImportFrom handled separately)
    FORBIDDEN_NODES = {
        ast.Global, ast.Nonlocal, ast.Delete
    }
    
    @classmethod
    def validate_code(cls, code: str) -> bool:
        """
        Validate rule code for safety
        
        Args:
            code: Python code string to validate
            
        Returns:
            bool: True if code is safe to execute
            
        Raises:
            ValueError: If code contains unsafe constructs
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in rule code: {e}")
        
        # Check for forbidden nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Check if all imports are allowed
                for alias in node.names:
                    if alias.name not in cls.ALLOWED_IMPORTS:
                        raise ValueError(f"Forbidden import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                # Check if importing from allowed modules
                if node.module not in cls.ALLOWED_IMPORTS:
                    raise ValueError(f"Forbidden import from: {node.module}")
            elif type(node) in cls.FORBIDDEN_NODES:
                raise ValueError(f"Forbidden construct: {type(node).__name__}")
            
            # Check function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in cls.ALLOWED_BUILTINS:
                        # Check if it's an allowed library function
                        allowed = False
                        for module, functions in cls.ALLOWED_IMPORTS.items():
                            if func_name in functions:
                                allowed = True
                                break
                        if not allowed:
                            raise ValueError(f"Forbidden function call: {func_name}")
            
            # Check attribute access
            if isinstance(node, ast.Attribute):
                # Only allow specific attribute patterns
                if isinstance(node.value, ast.Name):
                    obj_name = node.value.id
                    attr_name = node.attr
                    # Allow agent attributes, standard dict/list methods, and allowed module attributes
                    allowed = (
                        obj_name in ['agent', 'model', 'params'] or
                        attr_name in ['get', 'keys', 'values', 'items', 'append', 'copy'] or
                        (obj_name in cls.ALLOWED_IMPORTS and attr_name in cls.ALLOWED_IMPORTS[obj_name])
                    )
                    if not allowed:
                        raise ValueError(f"Forbidden attribute access: {obj_name}.{attr_name}")
        
        return True

class LLMRuleEngine:
    """Engine for creating and executing LLM-generated rules"""
    
    def __init__(self):
        self.custom_rules: Dict[str, Callable] = {}
        self.rule_metadata: Dict[str, Dict] = {}
    
    def create_rule_from_code(self, rule_name: str, rule_code: str, 
                             description: str = "", parameters: Dict[str, Any] = None) -> bool:
        """
        Create a custom rule from LLM-generated code
        
        Args:
            rule_name: Name for the new rule
            rule_code: Python code for the rule function
            description: Human-readable description
            parameters: Expected parameters and their types
            
        Returns:
            bool: True if rule was created successfully
            
        Raises:
            ValueError: If code is unsafe or invalid
        """
        # Validate the code
        SafeRuleValidator.validate_code(rule_code)
        
        # Ensure the code defines a function with the rule name
        if f"def {rule_name}(" not in rule_code:
            raise ValueError(f"Code must define a function named '{rule_name}'")
        
        # Create safe execution environment
        # Provide allowed modules directly to avoid import issues
        safe_globals = {
            '__builtins__': {
                name: __builtins__[name] for name in SafeRuleValidator.ALLOWED_BUILTINS
            },
            'copy': copy,
            'random': __import__('random'),
            'math': __import__('math')
        }
        
        # Execute the code to create the function
        try:
            exec(rule_code, safe_globals)
            rule_function = safe_globals[rule_name]
        except Exception as e:
            raise ValueError(f"Error creating rule function: {e}")
        
        # Validate function signature
        sig = inspect.signature(rule_function)
        if len(sig.parameters) < 2:
            raise ValueError("Rule function must accept at least (model, params) arguments")
        
        # Store the rule
        self.custom_rules[rule_name] = rule_function
        self.rule_metadata[rule_name] = {
            'description': description,
            'parameters': parameters or {},
            'code': rule_code,
            'signature': str(sig)
        }
        
        return True
    
    def create_rule_from_dsl(self, rule_name: str, rule_dsl: Dict[str, Any]) -> bool:
        """
        Create a rule from Domain Specific Language description
        
        Args:
            rule_name: Name for the new rule
            rule_dsl: DSL description of the rule
            
        Returns:
            bool: True if rule was created successfully
            
        Example DSL:
        {
            "description": "Agents seek food when hungry",
            "conditions": [
                "agent['type'] == 'animal'",
                "agent['energy'] < 10"
            ],
            "actions": [
                "move_toward_food(agent, model)",
                "agent['energy'] += 1"
            ],
            "parameters": {
                "energy_threshold": 10,
                "food_type": "grass"
            }
        }
        """
        # Extract DSL components
        description = rule_dsl.get('description', '')
        conditions = rule_dsl.get('conditions', [])
        actions = rule_dsl.get('actions', [])
        parameters = rule_dsl.get('parameters', {})
        
        # Generate Python code from DSL
        code_lines = [
            f"def {rule_name}(model, params):",
            "    \"\"\"" + description + "\"\"\"",
            "    new_model = copy.deepcopy(model)",
            "    ",
            "    for agent in new_model['agents']:",
            "        if not agent['alive']:",
            "            continue",
            "        ",
            "        # Check conditions"
        ]
        
        # Add conditions
        if conditions:
            code_lines.append("        if " + " and ".join(f"({cond})" for cond in conditions) + ":")
            # Add actions with proper indentation
            for action in actions:
                code_lines.append(f"            {action}")
        else:
            # No conditions, apply actions to all agents
            for action in actions:
                code_lines.append(f"        {action}")
        
        code_lines.extend([
            "    ",
            "    return new_model"
        ])
        
        rule_code = "\n".join(code_lines)
        
        return self.create_rule_from_code(rule_name, rule_code, description, parameters)
    
    def get_rule(self, rule_name: str) -> Callable:
        """Get a custom rule function"""
        if rule_name not in self.custom_rules:
            raise ValueError(f"Custom rule '{rule_name}' not found")
        return self.custom_rules[rule_name]
    
    def list_rules(self) -> Dict[str, Dict]:
        """List all custom rules with metadata"""
        return self.rule_metadata.copy()
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a custom rule"""
        if rule_name in self.custom_rules:
            del self.custom_rules[rule_name]
            del self.rule_metadata[rule_name]
            return True
        return False

# Global instance
rule_engine = LLMRuleEngine()

def add_custom_rule(model, rule_name: str, rule_definition, rule_type: str = "code"):
    """
    Add a custom rule to the model
    
    Args:
        model: Model dictionary
        rule_name: Name for the new rule
        rule_definition: Either code string or DSL dictionary
        rule_type: "code" or "dsl"
        
    Returns:
        model: Updated model with custom rule available
    """
    new_model = copy.deepcopy(model)
    
    if rule_type == "code":
        rule_engine.create_rule_from_code(rule_name, rule_definition)
    elif rule_type == "dsl":
        rule_engine.create_rule_from_dsl(rule_name, rule_definition)
    else:
        raise ValueError("rule_type must be 'code' or 'dsl'")
    
    return new_model

def execute_custom_rule(model, rule_name: str, params: Dict[str, Any]):
    """
    Execute a custom rule
    
    Args:
        model: Model dictionary
        rule_name: Name of custom rule to execute
        params: Parameters for the rule
        
    Returns:
        model: Updated model dictionary
    """
    rule_function = rule_engine.get_rule(rule_name)
    return rule_function(model, params)
