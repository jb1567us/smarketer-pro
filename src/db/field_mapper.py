"""
Custom field mapping system for flexible data transformation.
"""
from typing import Dict, List, Any, Callable
import re

class FieldMapper:
    """Manages custom field mappings and transformations."""
    
    def __init__(self):
        self.mappings: Dict[str, str] = {}
        self.transformations: Dict[str, Callable] = {}
        self.templates: Dict[str, Dict] = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict]:
        """Load default mapping templates for popular CRMs."""
        return {
            'salesforce_lead': {
                'name': 'Name',
                'company': 'Company',
                'title': 'Title',
                'email': 'Email',
                'phone': 'Phone',
                'website': 'Website'
            },
            'hubspot_contact': {
                'email': 'Email',
                'name': 'First Name',
                'company': 'Company Name',
                'title': 'Job Title',
                'phone': 'Phone Number'
            },
            'generic': {
                'name': 'name',
                'email': 'email',
                'company': 'company',
                'title': 'title'
            }
        }
    
    def load_template(self, template_name: str):
        """Load a predefined mapping template."""
        if template_name in self.templates:
            self.mappings = self.templates[template_name].copy()
            return True
        return False
    
    def add_mapping(self, source_field: str, target_field: str):
        """Add a custom field mapping."""
        self.mappings[source_field] = target_field
    
    def add_transformation(self, field: str, transform_func: Callable):
        """Add a transformation function for a field."""
        self.transformations[field] = transform_func
    
    def remove_mapping(self, source_field: str):
        """Remove a field mapping."""
        if source_field in self.mappings:
            del self.mappings[source_field]
    
    def apply_mappings(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply mappings and transformations to data."""
        if not data:
            return []
        
        mapped_data = []
        for record in data:
            mapped_record = {}
            
            # Apply mappings
            for source_field, target_field in self.mappings.items():
                if source_field in record:
                    value = record[source_field]
                    
                    # Apply transformation if exists
                    if source_field in self.transformations:
                        value = self.transformations[source_field](value)
                    
                    mapped_record[target_field] = value
            
            # Include unmapped fields if they don't conflict
            for key, value in record.items():
                if key not in self.mappings and key not in mapped_record:
                    mapped_record[key] = value
            
            mapped_data.append(mapped_record)
        
        return mapped_data
    
    def get_mappings(self) -> Dict[str, str]:
        """Get current mappings."""
        return self.mappings.copy()
    
    def clear_mappings(self):
        """Clear all mappings."""
        self.mappings.clear()
        self.transformations.clear()

# Common transformation functions
class Transformations:
    """Common data transformation functions."""
    
    @staticmethod
    def uppercase(value: str) -> str:
        """Convert to uppercase."""
        return str(value).upper() if value else ""
    
    @staticmethod
    def lowercase(value: str) -> str:
        """Convert to lowercase."""
        return str(value).lower() if value else ""
    
    @staticmethod
    def title_case(value: str) -> str:
        """Convert to title case."""
        return str(value).title() if value else ""
    
    @staticmethod
    def extract_domain(email: str) -> str:
        """Extract domain from email."""
        if not email or '@' not in email:
            return ""
        return email.split('@')[1]
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number (US format)."""
        if not phone:
            return ""
        # Remove non-digits
        digits = re.sub(r'\D', '', str(phone))
        # Format as (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone
    
    @staticmethod
    def linkedin_url(handle: str) -> str:
        """Convert handle to full LinkedIn URL."""
        if not handle:
            return ""
        if handle.startswith('http'):
            return handle
        clean = handle.replace('@', '').strip('/')
        return f"https://linkedin.com/in/{clean}"
