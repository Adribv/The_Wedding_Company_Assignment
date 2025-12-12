import re
from typing import Optional


def sanitize_organization_name(name: str) -> str:
    """
    Sanitize organization name to create a valid MongoDB collection name.
    Rules:
    - Must start with a letter or underscore
    - Can contain letters, digits, underscores
    - Convert to lowercase
    - Replace invalid characters with underscores
    - Remove leading/trailing underscores
    - Ensure it starts with 'org_'
    """
    # Convert to lowercase
    sanitized = name.lower().strip()
    
    # Replace spaces and invalid characters with underscores
    sanitized = re.sub(r'[^a-z0-9_]', '_', sanitized)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it starts with a letter or underscore
    if sanitized and not re.match(r'^[a-z_]', sanitized):
        sanitized = f"org_{sanitized}"
    
    # Ensure it starts with 'org_'
    if not sanitized.startswith('org_'):
        sanitized = f"org_{sanitized}"
    
    # Ensure minimum length
    if len(sanitized) < 4:  # "org_" minimum
        sanitized = f"org_{sanitized}"
    
    return sanitized


def validate_collection_name(name: str) -> bool:
    """Validate if a collection name is valid for MongoDB."""
    if not name or len(name) == 0:
        return False
    
    # MongoDB collection name rules
    # Cannot be empty, cannot contain $, cannot start with system.
    if name.startswith('system.'):
        return False
    
    if '$' in name:
        return False
    
    return True

