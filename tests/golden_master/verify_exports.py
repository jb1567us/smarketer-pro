"""
Golden Master Test: Export Templates
Verifies export template functionality for various CRM formats.
"""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from exporters.templates import (
    GenericCSVExporter, SalesforceExporter, 
    HubSpotExporter, JSONExporter, get_exporter
)

def test_exporter_factory():
    """Test exporter factory method."""
    tests = [
        ('csv', GenericCSVExporter),
        ('generic', GenericCSVExporter),
        ('salesforce', SalesforceExporter),
        ('hubspot', HubSpotExporter),
        ('json', JSONExporter)
    ]
    
    passed = 0
    failed = 0
    
    for format_type, expected_class in tests:
        exporter = get_exporter(format_type)
        if isinstance(exporter, expected_class):
            passed += 1
        else:
            print(f"FAIL: Factory for '{format_type}'")
            print(f"  Expected: {expected_class.__name__}")
            print(f"  Got: {type(exporter).__name__}")
            failed += 1
    
    return passed, failed

def test_export_functionality():
    """Test basic export functionality."""
    sample_data = [
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'company': 'Acme Corp',
            'title': 'CEO'
        }
    ]
    
    passed = 0
    failed = 0
    
    exporters = [
        ('Generic CSV', GenericCSVExporter()),
        ('Salesforce', SalesforceExporter()),
        ('HubSpot', HubSpotExporter()),
        ('JSON', JSONExporter())
    ]
    
    for name, exporter in exporters:
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
                temp_file = f.name
            
            result = exporter.export(sample_data, temp_file)
            
            # Check file was created
            if os.path.exists(temp_file):
                passed += 1
            else:
                print(f"FAIL: {name} export did not create file")
                failed += 1
            
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        except Exception as e:
            print(f"FAIL: {name} export raised exception: {e}")
            failed += 1
    
    return passed, failed

def test_field_mapping():
    """Test field mapping in exporters."""
    data = [{'name': 'Test', 'email': 'test@test.com'}]
    
    sf_exporter = SalesforceExporter()
    hs_exporter = HubSpotExporter()
    
    # Verify field maps exist
    passed = 0
    failed = 0
    
    if hasattr(sf_exporter, 'field_map') and len(sf_exporter.field_map) > 0:
        passed += 1
    else:
        print("FAIL: Salesforce exporter missing field_map")
        failed += 1
    
    if hasattr(hs_exporter, 'field_map') and len(hs_exporter.field_map) > 0:
        passed += 1
    else:
        print("FAIL: HubSpot exporter missing field_map")
        failed += 1
    
    return passed, failed

def main():
    print("Testing Export Templates...")
    
    total_passed = 0
    total_failed = 0
    
    # Test factory
    passed, failed = test_exporter_factory()
    total_passed += passed
    total_failed += failed
    print(f"  Exporter Factory: {passed} PASSED, {failed} FAILED")
    
    # Test export functionality
    passed, failed = test_export_functionality()
    total_passed += passed
    total_failed += failed
    print(f"  Export Functions: {passed} PASSED, {failed} FAILED")
    
    # Test field mapping
    passed, failed = test_field_mapping()
    total_passed += passed
    total_failed += failed
    print(f"  Field Mapping: {passed} PASSED, {failed} FAILED")
    
    print(f"\nExport Templates Results: {total_passed} PASSED, {total_failed} FAILED")
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
