from datamodel_code_generator import InputFileType, generate, DataModelType
from pathlib import Path

from cdf import VERSION
    
import re

def _convert_docstrings_to_comments(file_path: Path):
    """
    Converts striple quote comments to inline comments for easier readabily in type hints
    """
    content = file_path.read_text()
    
    # Pattern that captures field with docstring on next lines
    # This handles both single-line and multi-line type hints
    pattern = r'(\s+)(\w+): (.+?)\n(\s+)"""\n\4(.+?)\n\4"""'
    
    def replace_with_comment(match):
        indent = match.group(1)
        field_name = match.group(2)
        type_hint = match.group(3)
        description = match.group(5)
        
        # Check if type_hint ends with a bracket (multi-line type)
        if type_hint.strip().endswith(']'):
            # Multi-line: put comment after the closing bracket
            return f'{indent}{field_name}: {type_hint}  # {description}'
        else:
            # Single-line: straightforward
            return f'{indent}{field_name}: {type_hint}  # {description}'
    
    content = re.sub(pattern, replace_with_comment, content, flags=re.DOTALL)
    
    file_path.write_text(content)

# Create a path object
output_path = f"cdf/domain/latest"
path = Path(output_path).mkdir(exist_ok=True)

for file_type in ['event', 'match', 'meta', 'skeletal', 'tracking', 'video']:
    output_file = output_path / Path(f'{file_type}.py')
    generate(
        input_=Path(f'cdf/files/v{VERSION}/schema/{file_type}.json'),
        input_file_type=InputFileType.JsonSchema,
        output=output_file,
        output_model_type=DataModelType.TypingTypedDict,
        use_field_description=True,
        field_constraints=True,  
    )

    _convert_docstrings_to_comments(output_file)