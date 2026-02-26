"""
Test script to verify all Python imports work correctly.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

def test_imports():
    """Test all critical imports."""
    errors = []
    
    print("Testing Python imports...\n")
    
    # Core ML
    tests = [
        ("torch", "PyTorch"),
        ("torchvision", "TorchVision"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        
        # API
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        
        # Database
        ("sqlalchemy", "SQLAlchemy"),
        ("psycopg2", "psycopg2-binary"),
        
        # Security
        ("passlib", "Passlib"),
        ("jose", "python-jose"),
        
        # Logging
        ("loguru", "Loguru"),
        
        # NLP
        ("nltk", "NLTK"),
        
        # Utilities
        ("dotenv", "python-dotenv"),
    ]
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            errors.append((name, str(e)))
    
    # Test project imports
    print("\nTesting project modules...\n")
    
    project_tests = [
        ("models.encoder", "Image Encoder"),
        ("models.decoder", "Transformer Decoder"),
        ("models.captioning_model", "Captioning Model"),
        ("training.vocabulary", "Vocabulary"),
        ("training.dataset", "Dataset"),
        ("inference.predictor", "Predictor"),
        ("api.main", "FastAPI App"),
        ("database.models", "Database Models"),
    ]
    
    for module, name in project_tests:
        try:
            __import__(module)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            errors.append((name, str(e)))
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"❌ {len(errors)} import errors found:\n")
        for name, error in errors:
            print(f"  - {name}: {error}")
        return False
    else:
        print("✅ All imports successful!")
        return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
