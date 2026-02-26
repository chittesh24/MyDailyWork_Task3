#!/usr/bin/env python3
"""
Complete project validation script.
Checks all files, dependencies, and configurations.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Tuple

class ProjectValidator:
    """Validate project structure and dependencies."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
    
    def validate_structure(self) -> bool:
        """Validate project directory structure."""
        print("\n" + "="*60)
        print("VALIDATING PROJECT STRUCTURE")
        print("="*60)
        
        required_dirs = [
            "backend",
            "backend/models",
            "backend/training",
            "backend/inference",
            "backend/api",
            "backend/database",
            "frontend",
            "frontend/app",
            "frontend/components",
            "scripts",
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"✅ {dir_path}")
            else:
                print(f"❌ {dir_path} - MISSING")
                self.errors.append(f"Missing directory: {dir_path}")
        
        return len(self.errors) == 0
    
    def validate_files(self) -> bool:
        """Validate critical files exist."""
        print("\n" + "="*60)
        print("VALIDATING CRITICAL FILES")
        print("="*60)
        
        required_files = [
            "backend/requirements.txt",
            "backend/.env.example",
            "backend/api/main.py",
            "backend/models/encoder.py",
            "backend/models/decoder.py",
            "frontend/package.json",
            "frontend/app/page.tsx",
            "docker-compose.yml",
            "README.md",
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - MISSING")
                self.errors.append(f"Missing file: {file_path}")
        
        return len(self.errors) == 0
    
    def validate_dependencies(self) -> bool:
        """Check if requirements.txt is valid."""
        print("\n" + "="*60)
        print("VALIDATING DEPENDENCIES")
        print("="*60)
        
        req_file = self.project_root / "backend" / "requirements.txt"
        
        if not req_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            with open(req_file) as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            
            print(f"✅ Found {len(lines)} dependencies")
            
            # Check for critical packages
            critical = ['torch', 'fastapi', 'sqlalchemy', 'pydantic']
            for pkg in critical:
                if any(pkg in line.lower() for line in lines):
                    print(f"✅ {pkg}")
                else:
                    print(f"⚠️  {pkg} not found")
                    self.warnings.append(f"Missing critical package: {pkg}")
            
            return True
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
            self.errors.append(str(e))
            return False
    
    def validate_env_example(self) -> bool:
        """Validate .env.example exists and has required vars."""
        print("\n" + "="*60)
        print("VALIDATING ENVIRONMENT CONFIG")
        print("="*60)
        
        env_file = self.project_root / "backend" / ".env.example"
        
        if not env_file.exists():
            print("❌ .env.example not found")
            self.errors.append("Missing .env.example")
            return False
        
        try:
            with open(env_file) as f:
                content = f.read()
            
            required_vars = [
                'DATABASE_URL',
                'SECRET_KEY',
                'MODEL_CHECKPOINT_PATH',
                'VOCAB_PATH',
            ]
            
            for var in required_vars:
                if var in content:
                    print(f"✅ {var}")
                else:
                    print(f"❌ {var} - MISSING")
                    self.errors.append(f"Missing env var: {var}")
            
            return len(self.errors) == 0
        except Exception as e:
            print(f"❌ Error: {e}")
            self.errors.append(str(e))
            return False
    
    def validate_docker(self) -> bool:
        """Validate Docker configuration."""
        print("\n" + "="*60)
        print("VALIDATING DOCKER CONFIGURATION")
        print("="*60)
        
        docker_compose = self.project_root / "docker-compose.yml"
        dockerfile_backend = self.project_root / "Dockerfile"
        dockerfile_frontend = self.project_root / "frontend" / "Dockerfile"
        
        files = [
            (docker_compose, "docker-compose.yml"),
            (dockerfile_backend, "Dockerfile (backend)"),
            (dockerfile_frontend, "frontend/Dockerfile"),
        ]
        
        all_exist = True
        for file_path, name in files:
            if file_path.exists():
                print(f"✅ {name}")
            else:
                print(f"❌ {name} - MISSING")
                self.warnings.append(f"Missing: {name}")
                all_exist = False
        
        return all_exist
    
    def validate_scripts(self) -> bool:
        """Validate automation scripts."""
        print("\n" + "="*60)
        print("VALIDATING AUTOMATION SCRIPTS")
        print("="*60)
        
        scripts = [
            "train_coco.sh",
            "train_flickr8k.sh",
            "train_coco.py",
            "compare_models.py",
            "benchmark.py",
            "deploy_render.sh",
            "deploy_vercel.sh",
            "setup_free_tier.py",
        ]
        
        scripts_dir = self.project_root / "scripts"
        
        if not scripts_dir.exists():
            print("❌ scripts directory not found")
            return False
        
        for script in scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                print(f"✅ {script}")
            else:
                print(f"⚠️  {script} - MISSING")
                self.warnings.append(f"Missing script: {script}")
        
        return True
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
            print("\nProject is ready for deployment!")
        elif not self.errors:
            print("\n✅ No critical errors found")
            print("⚠️  Some warnings - review above")
        else:
            print("\n❌ Critical errors found - fix before deployment")
        
        return len(self.errors) == 0
    
    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("="*60)
        print("PROJECT VALIDATION")
        print("="*60)
        
        self.validate_structure()
        self.validate_files()
        self.validate_dependencies()
        self.validate_env_example()
        self.validate_docker()
        self.validate_scripts()
        
        return self.print_summary()


def main():
    validator = ProjectValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
