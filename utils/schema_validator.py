#!/usr/bin/env python3
"""
Schema Validator for Memory Layer Data.

Validates STM, MTM, LTM data against JSON schemas.
"""

import json
from typing import Dict, Any, List, Tuple
from pathlib import Path


class SchemaValidator:
    """Validates data against JSON schemas."""
    
    def __init__(self, schema_dir: str = "utils/schema"):
        self.schema_dir = Path(schema_dir)
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load all schemas."""
        schemas = {}
        for name in ['stm', 'mtm', 'ltm']:
            schema_file = self.schema_dir / f"{name}.json"
            with open(schema_file, 'r') as f:
                schemas[name] = json.load(f)
        return schemas
    
    def validate_stm(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate STM data."""
        return self._validate(data, self.schemas['stm'], 'STM')
    
    def validate_mtm(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate MTM data."""
        return self._validate(data, self.schemas['mtm'], 'MTM')
    
    def validate_ltm(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate LTM data."""
        return self._validate(data, self.schemas['ltm'], 'LTM')
    
    def _validate(self, data: Dict[str, Any], schema: Dict, name: str) -> Tuple[bool, List[str]]:
        """Generic validation against schema."""
        errors = []
        
        # Check required top-level fields
        required = schema.get('required', [])
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check metadata if present
        if 'metadata' in data and 'metadata' in schema['properties']:
            metadata_schema = schema['properties']['metadata']
            metadata_required = metadata_schema.get('required', [])
            
            for field in metadata_required:
                if field not in data['metadata']:
                    errors.append(f"Missing required metadata field: {field}")
        
        # Type checks
        properties = schema.get('properties', {})
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get('type')
                actual_value = data[field]
                
                if expected_type == 'string' and not isinstance(actual_value, str):
                    errors.append(f"Field '{field}' should be string, got {type(actual_value).__name__}")
                elif expected_type == 'integer' and not isinstance(actual_value, int):
                    errors.append(f"Field '{field}' should be integer, got {type(actual_value).__name__}")
                elif expected_type == 'object' and not isinstance(actual_value, dict):
                    errors.append(f"Field '{field}' should be object, got {type(actual_value).__name__}")
                elif expected_type == 'array' and not isinstance(actual_value, list):
                    errors.append(f"Field '{field}' should be array, got {type(actual_value).__name__}")
                
                # Check enums
                if 'enum' in field_schema:
                    if actual_value not in field_schema['enum']:
                        errors.append(f"Field '{field}' value '{actual_value}' not in allowed values: {field_schema['enum']}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_file(self, file_path: str, data_type: str) -> Tuple[int, int, List[str]]:
        """
        Validate entire data file.
        
        Args:
            file_path: Path to JSON file
            data_type: 'stm', 'mtm', or 'ltm'
            
        Returns:
            (valid_count, total_count, all_errors)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            data = [data]
        
        validator_func = {
            'stm': self.validate_stm,
            'mtm': self.validate_mtm,
            'ltm': self.validate_ltm
        }[data_type]
        
        valid_count = 0
        all_errors = []
        
        for idx, item in enumerate(data):
            is_valid, errors = validator_func(item)
            if is_valid:
                valid_count += 1
            else:
                all_errors.append(f"Item {idx}: {'; '.join(errors)}")
        
        return valid_count, len(data), all_errors


def main():
    """Test validation."""
    print("╔" + "="*78 + "╗")
    print("║" + " "*28 + "SCHEMA VALIDATION" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    
    validator = SchemaValidator()
    
    # Test with current data
    files_to_test = [
        ('data/stm.json', 'stm', 'STM'),
        ('data/mtm.json', 'mtm', 'MTM'),
        ('data/ltm.json', 'ltm', 'LTM'),
    ]
    
    for file_path, data_type, name in files_to_test:
        try:
            valid, total, errors = validator.validate_file(file_path, data_type)
            
            print(f"\n📋 {name} ({file_path}):")
            print(f"   Valid: {valid}/{total}")
            
            if errors:
                print(f"   ❌ Errors found:")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"      • {error}")
                if len(errors) > 5:
                    print(f"      ... and {len(errors)-5} more errors")
            else:
                print(f"   ✅ All items valid!")
                
        except FileNotFoundError:
            print(f"\n📋 {name}: File not found")
        except Exception as e:
            print(f"\n📋 {name}: Error - {e}")
    
    print("\n" + "="*80)
    print("💡 To fix validation errors, regenerate data with updated script")
    print("="*80)


if __name__ == "__main__":
    main()
