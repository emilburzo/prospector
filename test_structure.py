#!/usr/bin/env python3
"""
Simple test script to verify the application structure
"""

import sys

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.config import get_settings
        from app.database import Base, get_db
        from app.models import JobApplication, JobLead, Resume
        from app.schemas import JobApplicationCreate, JobLeadCreate, ResumeCreate
        from app.services import OpenRouterService
        from app.routers import applications, leads, resumes
        from app.main import app
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_api_schema():
    """Test that API schema is valid"""
    try:
        from app.main import app
        schema = app.openapi()
        paths = schema.get('paths', {})
        print(f"✓ API has {len(paths)} endpoints")
        
        # Check key endpoints exist
        required_paths = [
            '/api/applications/',
            '/api/leads/',
            '/api/resumes/',
            '/health'
        ]
        
        for path in required_paths:
            if path not in paths:
                print(f"✗ Missing required endpoint: {path}")
                return False
        
        print("✓ All required endpoints present")
        return True
    except Exception as e:
        print(f"✗ API schema test failed: {e}")
        return False


def test_models():
    """Test that models are properly defined"""
    try:
        from app.models import JobApplication, JobLead, Resume
        from app.database import Base
        
        # Check that models are properly registered
        tables = Base.metadata.tables
        required_tables = ['job_applications', 'job_leads', 'resumes']
        
        for table in required_tables:
            if table not in tables:
                print(f"✗ Missing table: {table}")
                return False
        
        print(f"✓ All {len(required_tables)} database tables defined")
        return True
    except Exception as e:
        print(f"✗ Models test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Running application structure tests...\n")
    
    tests = [
        test_imports,
        test_api_schema,
        test_models
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
