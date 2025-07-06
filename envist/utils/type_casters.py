"""Type casting utilities for environment variables with nested type support"""

import json
import re
from typing import Any, Callable, Dict, List, Set, Tuple, Union

from ..core.exceptions import EnvistCastError


class TypeCaster:
    """Handles type casting for environment variables including nested types"""

    def cast_value(self, value: Any, cast_type: Union[str, Callable]) -> Any:
        """Cast value to specified type

        Args:
            value: Value to cast
            cast_type: Type to cast to (string name or callable)

        Returns:
            Cast value

        Raises:
            EnvistCastError: If casting fails
        """
        try:
            if isinstance(cast_type, str):
                return self._cast_by_string(value, cast_type)
            elif callable(cast_type):
                return cast_type(value)
            else:
                raise EnvistCastError(f"Invalid cast type: {cast_type}")
        except Exception as e:
            raise EnvistCastError(f'Unable to cast "{value}" to "{cast_type}": {e}')

    def _cast_by_string(self, value: Any, cast_type: str) -> Any:
        """Cast value based on string type name with nested type support"""
        # Parse nested type syntax
        parsed_type = self._parse_type_syntax(cast_type)
        return self._apply_type_casting(value, parsed_type)

    def _parse_type_syntax(self, type_str: str) -> Dict[str, Any]:
        """Parse type syntax like 'list<int>' or 'dict<str, list<int>>'

        Returns:
            Dictionary representing the parsed type structure
        """
        type_str = type_str.strip()

        # Check for nested types with angle brackets
        if "<" in type_str and ">" in type_str:
            # Extract base type and nested types
            base_match = re.match(r"^(\w+)<(.+)>$", type_str)
            if not base_match:
                raise EnvistCastError(f"Invalid type syntax: {type_str}")

            base_type = base_match.group(1).lower()
            inner_types = base_match.group(2)

            # Parse inner types
            if base_type in ("list", "set", "tuple"):
                # Single inner type
                inner_type = self._parse_type_syntax(inner_types.strip())
                return {"type": base_type, "inner_type": inner_type}
            elif base_type == "dict":
                # Two inner types separated by comma
                inner_parts = self._split_type_args(inner_types)
                if len(inner_parts) != 2:
                    raise EnvistCastError(
                        f"Dict type requires exactly 2 type arguments: {type_str}"
                    )

                key_type = self._parse_type_syntax(inner_parts[0].strip())
                value_type = self._parse_type_syntax(inner_parts[1].strip())

                return {
                    "type": base_type,
                    "key_type": key_type,
                    "value_type": value_type,
                }
            else:
                raise EnvistCastError(f"Unsupported nested type: {base_type}")
        elif "<" in type_str or ">" in type_str:
            # Unmatched brackets are invalid
            raise EnvistCastError(f"Invalid type syntax: {type_str}")
        else:
            # Simple type - validate it's supported
            simple_type = type_str.lower()
            supported_types = {
                "int", "float", "bool", "str", "list", "array", "dict", 
                "tuple", "set", "csv", "comma_separated", "json"
            }
            if simple_type not in supported_types:
                raise EnvistCastError(f"Unsupported type: {simple_type}")
            return {"type": simple_type}

    def _split_type_args(self, args_str: str) -> List[str]:
        """Split type arguments respecting nested brackets"""
        if not args_str or not args_str.strip():
            return []
            
        parts = []
        current = ""
        bracket_count = 0

        for char in args_str:
            if char == "<":
                bracket_count += 1
                current += char
            elif char == ">":
                bracket_count -= 1
                current += char
            elif char == "," and bracket_count == 0:
                if current.strip():  # Only add non-empty parts
                    parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():  # Only add non-empty parts
            parts.append(current.strip())

        return parts

    def _apply_type_casting(self, value: Any, type_info: Dict[str, Any]) -> Any:
        """Apply type casting based on parsed type information"""
        base_type = type_info["type"]

        # Check for unsupported nested types first
        if "inner_types" in type_info or "inner_type" in type_info or "key_type" in type_info:
            # This is a nested type, check if base type is supported for nesting
            supported_nested_types = {"list", "set", "tuple", "dict"}
            if base_type not in supported_nested_types:
                raise EnvistCastError(f"Unsupported nested type: {base_type}")

        # Handle nested types
        if "inner_type" in type_info:
            # List, Set, Tuple with single inner type
            collection = self._cast_to_smart_list(value)
            inner_type = type_info["inner_type"]

            casted_items = [
                self._apply_type_casting(item, inner_type) for item in collection
            ]

            if base_type == "list":
                return casted_items
            elif base_type == "set":
                return set(casted_items)
            elif base_type == "tuple":
                return tuple(casted_items)

        elif "key_type" in type_info and "value_type" in type_info:
            # Dict with key and value types
            dict_data = self._cast_to_smart_dict(value)
            key_type = type_info["key_type"]
            value_type = type_info["value_type"]

            casted_dict = {}
            for k, v in dict_data.items():
                casted_key = self._apply_type_casting(k, key_type)
                casted_value = self._apply_type_casting(v, value_type)
                casted_dict[casted_key] = casted_value

            return casted_dict
        else:
            # Simple type
            return self._cast_simple_type(value, base_type)

    def _cast_simple_type(self, value: Any, type_name: str) -> Any:
        """Cast to simple types"""
        if type_name == "int":
            return int(value)
        elif type_name == "float":
            return float(value)
        elif type_name == "bool":
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)
        elif type_name == "str":
            return str(value)
        elif type_name in ("list", "array"):
            return self._cast_to_smart_list(value)
        elif type_name == "dict":
            return self._cast_to_smart_dict(value)
        elif type_name == "tuple":
            return tuple(self._cast_to_smart_list(value))
        elif type_name == "set":
            return set(self._cast_to_smart_list(value))
        elif type_name in ("csv", "comma_separated"):
            return self._cast_to_csv(value)
        elif type_name == "json":
            return self._cast_to_json(value)
        else:
            raise EnvistCastError(f'"{type_name}" is not a valid cast type')

    def _cast_to_collection(self, value: Any, collection_type: str) -> List[Any]:
        """Cast value to a collection (list, set, tuple) and return as list"""
        if collection_type in ("list", "set", "tuple"):
            return self._cast_to_smart_list(value)
        else:
            raise EnvistCastError(f"Unsupported collection type: {collection_type}")

    def _cast_to_smart_list(self, value: Any) -> list:
        """Enhanced list casting that handles nested structures"""
        if isinstance(value, list):
            return value

        if not isinstance(value, str):
            return list(value)

        value = value.strip()

        # Try JSON parsing first for properly formatted JSON arrays
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Handle nested list notation like [[1,2,3],[4,5,6],[7,8,9]]
        # But first check if we have multiple top-level nested structures
        if value.startswith("[[") and value.endswith("]]"):
            # Check if this is multiple nested lists by using smart split
            top_level_items = self._smart_split(value, ",")
            if len(top_level_items) > 1:
                # Multiple nested structures, parse each separately
                result = []
                for item in top_level_items:
                    item = item.strip()
                    if item.startswith("[[") and item.endswith("]]"):
                        result.append(self._parse_nested_list(item))
                    elif item.startswith("[") and item.endswith("]"):
                        # Single nested list
                        result.append(self._cast_to_smart_list(item))
                    else:
                        result.append(item)
                return result
            else:
                # Single nested list structure
                return self._parse_nested_list(value)

        # Handle list of JSON objects like {"name":"John","role":"admin"},{"name":"Jane","role":"user"}
        if "{" in value and "}" in value:
            return self._parse_list_of_objects(value)

        # Handle simple bracket notation [1,2,3]
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]

        # Split by comma and clean up
        if not value.strip():
            return []

        items = self._smart_split(value, ",")
        result = []

        for item in items:
            item = item.strip()
            if item:
                # Remove quotes if present
                item = self._remove_quotes(item)
                result.append(item)

        return result

    def _parse_nested_list(self, value: str) -> list:
        """Parse nested list notation like [[1,2,3],[4,5,6],[7,8,9]]"""
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]  # Remove outer brackets

        # Split by inner list boundaries
        inner_lists = []
        current = ""
        bracket_count = 0

        for char in value:
            if char == "[":
                bracket_count += 1
                if bracket_count == 1:
                    current = ""
                else:
                    current += char
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    if current.strip():
                        # Parse the inner list content
                        inner_list_items = [
                            item.strip() for item in current.split(",") if item.strip()
                        ]
                        inner_lists.append(inner_list_items)
                    current = ""
                else:
                    current += char
            elif bracket_count > 0:
                current += char

        return inner_lists

    def _parse_list_of_objects(self, value: str) -> list:
        """Parse list of JSON objects"""
        objects = []
        current = ""
        brace_count = 0
        in_quotes = False
        quote_char = None

        for char in value:
            if char in "\"'":
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current += char
            elif not in_quotes:
                if char == "{":
                    brace_count += 1
                    current += char
                elif char == "}":
                    brace_count -= 1
                    current += char
                    if brace_count == 0:
                        # Complete object found
                        if current.strip():
                            try:
                                obj = json.loads(current.strip())
                                objects.append(obj)
                            except json.JSONDecodeError:
                                # Fallback to string if JSON parsing fails
                                objects.append(current.strip())
                        current = ""
                elif char == "," and brace_count == 0:
                    # Separator between objects
                    continue
                else:
                    current += char
            else:
                current += char

        # Handle any remaining content
        if current.strip():
            try:
                obj = json.loads(current.strip())
                objects.append(obj)
            except json.JSONDecodeError:
                objects.append(current.strip())

        return objects

    def _cast_to_smart_dict(self, value: Any) -> dict:
        """Enhanced dictionary casting that handles various formats"""
        if isinstance(value, dict):
            return value

        if not isinstance(value, str):
            return dict(value)

        value = value.strip()

        # Try JSON parsing first
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Handle key=value format like group1=[1,2,3],group2=[4,5,6]
        result = {}

        # Remove braces if present
        if value.startswith("{") and value.endswith("}"):
            value = value[1:-1]

        if not value:
            return {}

        # Smart split respecting brackets and quotes
        pairs = self._smart_split(value, ",")

        for pair in pairs:
            if "=" in pair:
                key, val = pair.split("=", 1)
                key = key.strip().strip("'\"")
                val = val.strip()

                # Handle list values like [1,2,3]
                if val.startswith("[") and val.endswith("]"):
                    val = self._cast_to_smart_list(val)
                else:
                    val = self._remove_quotes(val)

                result[key] = val
            elif ":" in pair:
                key, val = pair.split(":", 1)
                key = key.strip().strip("'\"")
                val = val.strip().strip("'\"")
                result[key] = val

        return result

    def _smart_split(self, text: str, delimiter: str) -> List[str]:
        """Smart split that respects brackets, braces, and quotes"""
        result = []
        current = ""
        bracket_count = 0
        brace_count = 0
        in_quotes = False
        quote_char = None

        for char in text:
            if char in "\"'":
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current += char
            elif not in_quotes:
                if char == "[":
                    bracket_count += 1
                    current += char
                elif char == "]":
                    bracket_count -= 1
                    current += char
                elif char == "{":
                    brace_count += 1
                    current += char
                elif char == "}":
                    brace_count -= 1
                    current += char
                elif char == delimiter and bracket_count == 0 and brace_count == 0:
                    if current.strip():
                        result.append(current.strip())
                    current = ""
                else:
                    current += char
            else:
                current += char

        if current.strip():
            result.append(current.strip())

        return result

    def _remove_quotes(self, value: str) -> str:
        """Remove surrounding quotes from value"""
        if len(value) >= 2:
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                return value[1:-1]
        return value

    def _parse_bracket_list(self, value: str) -> List[Any]:
        """Parse bracketed list notation like [1,2,3] or [[1,2],[3,4]]"""
        if not isinstance(value, str) or not value.strip():
            return []
            
        value = value.strip()
        
        # Simple case: no brackets, just return as is
        if not (value.startswith('[') and value.endswith(']')):
            return [value]
            
        # Remove outer brackets
        inner = value[1:-1].strip()
        if not inner:
            return []
            
        # Check if this is a nested list
        if inner.startswith('[') and ']' in inner:
            return self._parse_nested_bracket_structure(inner)
        else:
            # Simple list
            return self._smart_split(inner, ',')
    
    def _parse_nested_bracket_structure(self, value: str) -> List[List[Any]]:
        """Parse complex nested bracket structures"""
        if not value:
            return []
            
        result = []
        current_item = ""
        bracket_count = 0
        
        for char in value:
            if char == '[':
                bracket_count += 1
                current_item += char
            elif char == ']':
                bracket_count -= 1
                current_item += char
                if bracket_count == 0:
                    # Complete nested item
                    parsed_item = self._parse_bracket_list(current_item)
                    result.append(parsed_item)
                    current_item = ""
            elif char == ',' and bracket_count == 0:
                # Item separator at top level
                if current_item.strip():
                    result.append([current_item.strip()])
                current_item = ""
            else:
                current_item += char
                
        # Handle remaining item
        if current_item.strip():
            if current_item.startswith('[') and current_item.endswith(']'):
                result.append(self._parse_bracket_list(current_item))
            else:
                result.append([current_item.strip()])
                
        return result
    
    def _parse_dict_value(self, value: str) -> Any:
        """Parse dictionary values that could be lists, objects, or simple values"""
        value = value.strip()
        
        # List value like [1,2,3]
        if value.startswith('[') and value.endswith(']'):
            return self._parse_bracket_list(value)
        
        # JSON object value like {"key":"value"}  
        if value.startswith('{') and value.endswith('}'):
            try:
                return json.loads(value)
            except:
                return value
                
        # Simple value - remove quotes if present
        return self._remove_quotes(value)
    
    def _smart_split_dict_pairs(self, value: str) -> List[str]:
        """Split dictionary pairs accounting for nested structures"""
        if not value:
            return []
            
        pairs = []
        current_pair = ""
        bracket_count = 0
        brace_count = 0
        
        for char in value:
            if char == '[':
                bracket_count += 1
                current_pair += char
            elif char == ']':
                bracket_count -= 1  
                current_pair += char
            elif char == '{':
                brace_count += 1
                current_pair += char
            elif char == '}':
                brace_count -= 1
                current_pair += char
            elif char == ',' and bracket_count == 0 and brace_count == 0:
                # Top-level separator
                if current_pair.strip():
                    pairs.append(current_pair.strip())
                current_pair = ""
            else:
                current_pair += char
                
        # Handle remaining pair
        if current_pair.strip():
            pairs.append(current_pair.strip())
            
        return pairs

    # Public method aliases that tests expect
    def parse_type_syntax(self, type_str: str) -> Dict[str, Any]:
        """Public method for parsing type syntax (test compatibility)"""
        return self._parse_type_syntax(type_str)
    
    def split_type_args(self, args_str: str) -> List[str]:
        """Public method for splitting type arguments (test compatibility)"""
        return self._split_type_args(args_str)
    
    def apply_type_casting(self, value: Any, type_info: Union[Dict[str, Any], tuple]) -> Any:
        """Public method for applying type casting (test compatibility)"""
        if isinstance(type_info, tuple):
            # Handle tuple format (type_name, inner_types)
            type_name, inner_types = type_info
            if type_name in ("list", "set", "tuple") and inner_types:
                type_dict = {"type": type_name, "inner_type": {"type": inner_types[0] if inner_types else "str"}}
            elif type_name == "dict" and len(inner_types) >= 2:
                type_dict = {
                    "type": type_name,
                    "key_type": {"type": inner_types[0]},
                    "value_type": {"type": inner_types[1]}
                }
            else:
                type_dict = {"type": type_name}
            return self._apply_type_casting(value, type_dict)
        return self._apply_type_casting(value, type_info)
    
    def cast_to_smart_list(self, value: Any) -> list:
        """Public method for smart list casting (test compatibility)"""
        return self._cast_to_smart_list(value)
    
    def cast_to_smart_dict(self, value: Any) -> dict:
        """Public method for smart dict casting (test compatibility)"""
        return self._cast_to_smart_dict(value)
    
    def parse_nested_list(self, value: str) -> list:
        """Public method for parsing nested lists (test compatibility)"""
        return self._parse_nested_list(value)
    
    def parse_bracket_list(self, value: str) -> List[Any]:
        """Public method for parsing bracket lists (test compatibility)"""
        return self._parse_bracket_list(value)
    
    def smart_split(self, text: str, delimiter: str) -> List[str]:
        """Public method for smart splitting (test compatibility)"""
        return self._smart_split(text, delimiter)
    
    def smart_split_dict_pairs(self, value: str) -> List[str]:
        """Public method for smart splitting dict pairs (test compatibility)"""
        return self._smart_split_dict_pairs(value)
    
    def remove_quotes(self, value: str) -> str:
        """Public method for removing quotes (test compatibility)"""
        return self._remove_quotes(value)
    
    def cast_to_csv(self, value: str) -> list:
        """Public method for CSV casting (test compatibility)"""
        return self._cast_to_csv(value)
    
    def cast_to_json(self, value: str) -> Any:
        """Public method for JSON casting (test compatibility)"""
        return self._cast_to_json(value)
    
    def cast_to_list(self, value: str) -> list:
        """Public method for list casting (test compatibility)"""
        return self._cast_to_smart_list(value)
    
    def parse_dict_value(self, value: str) -> Any:
        """Public method for parsing dict values (test compatibility)"""
        return self._parse_dict_value(value)

    # Keep the legacy methods for backward compatibility
    def _cast_to_list(self, value: str) -> list:
        """Cast string to list (legacy method)"""
        return self._cast_to_smart_list(value)

    def _cast_to_dict(self, value: Any) -> dict:
        """Cast string to dictionary (legacy method)"""
        return self._cast_to_smart_dict(value)

    def _cast_to_csv(self, value: str) -> list:
        """Cast string to CSV list"""
        import csv
        import io

        if not isinstance(value, str):
            return list(value)

        reader = csv.reader(io.StringIO(value))
        return next(reader, [])

    def _cast_to_json(self, value: str) -> Any:
        """Cast string to JSON object"""
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise EnvistCastError(f"Invalid JSON format: {e}")

    # Legacy public method aliases for compatibility
    def cast_to_dict(self, value: Any) -> dict:
        """Legacy alias for _cast_to_smart_dict"""
        return self._cast_to_smart_dict(value)
