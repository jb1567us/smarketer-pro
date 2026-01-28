"""
Export template system for various CRM formats.
"""
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class BaseExporter:
    """Base class for all exporters."""
    
    def __init__(self):
        self.format_name = "Generic"
    
    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export data to specified format."""
        raise NotImplementedError("Subclasses must implement export()")
    
    def _sanitize_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert data to DataFrame and sanitize."""
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)

class GenericCSVExporter(BaseExporter):
    """Generic CSV export with all available fields."""
    
    def __init__(self):
        super().__init__()
        self.format_name = "Generic CSV"
    
    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export to generic CSV format."""
        df = self._sanitize_data(data)
        
        if df.empty:
            return f"No data to export to {output_path}"
        
        # Add export metadata
        df['exported_at'] = datetime.now().isoformat()
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return f"Exported {len(df)} records to {output_path}"

class SalesforceExporter(BaseExporter):
    """Salesforce-compatible CSV export."""
    
    def __init__(self):
        super().__init__()
        self.format_name = "Salesforce CSV"
        
        # Salesforce standard field mappings
        self.field_map = {
            'name': 'Name',
            'company': 'Company',
            'title': 'Title',
            'email': 'Email',
            'phone': 'Phone',
            'website': 'Website',
            'linkedin': 'LinkedIn__c',  # Custom field
            'location': 'City',
            'state': 'State',
            'country': 'Country',
            'industry': 'Industry',
            'description': 'Description'
        }
    
    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export to Salesforce CSV format."""
        df = self._sanitize_data(data)
        
        if df.empty:
            return f"No data to export to {output_path}"
        
        # Map fields to Salesforce schema
        mapped_df = pd.DataFrame()
        for source_field, sf_field in self.field_map.items():
            if source_field in df.columns:
                mapped_df[sf_field] = df[source_field]
        
        # Add required Salesforce fields
        mapped_df['LeadSource'] = 'B2B Outreach Tool'
        mapped_df['Status'] = 'New'
        
        # Salesforce requires specific date format
        if 'created_at' in df.columns:
            mapped_df['CreatedDate'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        mapped_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return f"Exported {len(mapped_df)} records to Salesforce format: {output_path}"

class HubSpotExporter(BaseExporter):
    """HubSpot-compatible CSV export."""
    
    def __init__(self):
        super().__init__()
        self.format_name = "HubSpot CSV"
        
        # HubSpot standard properties
        self.field_map = {
            'email': 'Email',
            'name': 'First Name',  # Will split if needed
            'company': 'Company Name',
            'title': 'Job Title',
            'phone': 'Phone Number',
            'website': 'Website URL',
            'linkedin': 'LinkedIn Profile',
            'location': 'City',
            'state': 'State/Region',
            'country': 'Country',
            'industry': 'Industry'
        }
    
    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export to HubSpot CSV format."""
        df = self._sanitize_data(data)
        
        if df.empty:
            return f"No data to export to {output_path}"
        
        # Map fields to HubSpot properties
        mapped_df = pd.DataFrame()
        for source_field, hs_field in self.field_map.items():
            if source_field in df.columns:
                mapped_df[hs_field] = df[source_field]
        
        # Split name into First Name / Last Name if present
        if 'name' in df.columns:
            names = df['name'].str.split(' ', n=1, expand=True)
            mapped_df['First Name'] = names[0] if 0 in names.columns else ''
            mapped_df['Last Name'] = names[1] if 1 in names.columns else ''
        
        # Add HubSpot metadata
        mapped_df['Lead Status'] = 'New'
        mapped_df['Lifecycle Stage'] = 'Lead'
        
        mapped_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return f"Exported {len(mapped_df)} records to HubSpot format: {output_path}"

class JSONExporter(BaseExporter):
    """JSON export for API integrations."""
    
    def __init__(self):
        super().__init__()
        self.format_name = "JSON"
    
    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export to JSON format."""
        import json
        
        if not data:
            return f"No data to export to {output_path}"
        
        # Add metadata
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'record_count': len(data),
            'records': data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return f"Exported {len(data)} records to JSON: {output_path}"

# Factory for getting exporters
def get_exporter(format_type: str) -> BaseExporter:
    """Factory method to get appropriate exporter."""
    exporters = {
        'csv': GenericCSVExporter(),
        'generic': GenericCSVExporter(),
        'salesforce': SalesforceExporter(),
        'hubspot': HubSpotExporter(),
        'json': JSONExporter()
    }
    
    return exporters.get(format_type.lower(), GenericCSVExporter())
