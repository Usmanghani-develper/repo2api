"""Python AST parser for function detection."""

import ast
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from inspect import signature, Parameter

from backend.models import FunctionInfo, FunctionParameter

logger = logging.getLogger(__name__)


class PythonParser:
    """Parser for Python files using AST."""
    
    def __init__(self, ignore_private: bool = True, ignore_magic: bool = True):
        """
        Initialize Python parser.
        
        Args:
            ignore_private: Whether to ignore private functions (starting with _)
            ignore_magic: Whether to ignore magic methods (like __init__)
        """
        self.ignore_private = ignore_private
        self.ignore_magic = ignore_magic
    
    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Parse a Python file and extract function information.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of FunctionInfo objects
        """
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_name = file_path.stem
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Skip if should ignore
                    if self.ignore_private and node.name.startswith('_'):
                        continue
                    if self.ignore_magic and node.name.startswith('__'):
                        continue
                    
                    func_info = self._extract_function_info(
                        node, 
                        file_path, 
                        module_name,
                        content
                    )
                    
                    if func_info:
                        functions.append(func_info)
        
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return functions
    
    def _extract_function_info(
        self,
        node: ast.FunctionDef,
        file_path: Path,
        module_name: str,
        source_code: str
    ) -> Optional[FunctionInfo]:
        """
        Extract function information from AST node.
        
        Args:
            node: AST FunctionDef node
            file_path: Path to source file
            module_name: Module name
            source_code: Full source code
            
        Returns:
            FunctionInfo object or None
        """
        try:
            # Extract parameters
            parameters = self._extract_parameters(node)
            
            # Extract return type annotation
            return_type = self._extract_return_type(node)
            
            # Extract docstring
            docstring = ast.get_docstring(node)
            
            # Check if async
            is_async = isinstance(node, ast.AsyncFunctionDef)
            
            return FunctionInfo(
                name=node.name,
                module=module_name,
                file_path=str(file_path),
                docstring=docstring,
                parameters=parameters,
                return_type=return_type,
                is_async=is_async,
                line_number=node.lineno
            )
        except Exception as e:
            logger.error(f"Error extracting function info for {node.name}: {e}")
            return None
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[FunctionParameter]:
        """
        Extract function parameters from AST node.
        
        Args:
            node: AST FunctionDef node
            
        Returns:
            List of FunctionParameter objects
        """
        parameters = []
        args = node.args
        
        # Get defaults
        defaults_count = len(args.defaults)
        total_args = len(args.args)
        required_count = total_args - defaults_count
        
        # Process regular arguments
        for i, arg in enumerate(args.args):
            # Skip 'self' and 'cls'
            if arg.arg in ('self', 'cls'):
                continue
            
            is_optional = i >= required_count
            default_value = None
            
            if is_optional:
                default_idx = i - required_count
                default_node = args.defaults[default_idx]
                default_value = self._extract_default_value(default_node)
            
            param_type = self._extract_annotation(arg.annotation)
            
            parameters.append(FunctionParameter(
                name=arg.arg,
                type=param_type,
                default=default_value,
                is_optional=is_optional
            ))
        
        # Process *args
        if args.vararg:
            parameters.append(FunctionParameter(
                name=f"*{args.vararg.arg}",
                type="tuple",
                is_optional=True
            ))
        
        # Process **kwargs
        if args.kwarg:
            parameters.append(FunctionParameter(
                name=f"**{args.kwarg.arg}",
                type="dict",
                is_optional=True
            ))
        
        return parameters
    
    def _extract_annotation(self, annotation: Optional[ast.expr]) -> str:
        """
        Extract type annotation from AST node.
        
        Args:
            annotation: AST annotation node
            
        Returns:
            Type string
        """
        if annotation is None:
            return "any"
        
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            elif isinstance(annotation, ast.Subscript):
                # Handle generic types like List[int]
                if isinstance(annotation.value, ast.Name):
                    base = annotation.value.id
                    return f"{base}[...]"
            
            # Fallback: try to unparse (Python 3.9+)
            return ast.unparse(annotation)
        except Exception:
            return "any"
    
    def _extract_default_value(self, node: ast.expr) -> Any:
        """
        Extract default value from AST node.
        
        Args:
            node: AST expression node
            
        Returns:
            Default value
        """
        try:
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.List):
                return "[]"
            elif isinstance(node, ast.Dict):
                return "{}"
            elif isinstance(node, ast.Tuple):
                return "()"
            elif isinstance(node, ast.Name):
                return node.id
            
            return None
        except Exception:
            return None
    
    def _extract_return_type(self, node: ast.FunctionDef) -> str:
        """
        Extract return type annotation from AST node.
        
        Args:
            node: AST FunctionDef node
            
        Returns:
            Return type string
        """
        if node.returns is None:
            return "any"
        
        return self._extract_annotation(node.returns)


class ParserFactory:
    """Factory for creating language-specific parsers."""
    
    _parsers = {
        'python': PythonParser
    }
    
    @classmethod
    def create_parser(cls, language: str = 'python'):
        """
        Create a parser for the specified language.
        
        Args:
            language: Programming language
            
        Returns:
            Parser instance
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in cls._parsers:
            raise ValueError(f"Unsupported language: {language}")
        
        return cls._parsers[language]()
    
    @classmethod
    def register_parser(cls, language: str, parser_class):
        """
        Register a new language parser.
        
        Args:
            language: Programming language name
            parser_class: Parser class
        """
        cls._parsers[language] = parser_class
    
    @classmethod
    def supported_languages(cls) -> List[str]:
        """Get list of supported languages."""
        return list(cls._parsers.keys())
