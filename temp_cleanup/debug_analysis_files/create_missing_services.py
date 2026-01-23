#!/usr/bin/env python3
"""
Quick script to create minimal working versions of the missing microservices
so we can start all 4 services immediately.
"""

import os

def create_loyalty_service():
    """Create loyalty service structure"""
    print("Creating loyalty service...")
    service_dir = "loyalty-service"
    os.makedirs(service_dir, exist_ok=True)
    os.makedirs(f"{service_dir}/loyalty", exist_ok=True)
    
    # Create manage.py
    manage_content = '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loyalty.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''
    
    with open(f"{service_dir}/manage.py", "w") as f:
        f.write(manage_content)
    
    # Create __init__.py
    with open(f"{service_dir}/loyalty/__init__.py", "w") as f:
        f.write("")
    
    print("Loyalty service created successfully!")

def create_ui_service():
    """Create UI service structure"""
    print("Creating UI service...")
    service_dir = "ui-service"
    os.makedirs(service_dir, exist_ok=True)
    os.makedirs(f"{service_dir}/ui", exist_ok=True)
    
    # Create manage.py
    manage_content = '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''
    
    with open(f"{service_dir}/manage.py", "w") as f:
        f.write(manage_content)
    
    # Create __init__.py
    with open(f"{service_dir}/ui/__init__.py", "w") as f:
        f.write("")
    
    print("UI service created successfully!")

def main():
    """Main function to create all missing services"""
    print("Creating missing microservices...")
    
    # Change to microservices directory
    if not os.path.exists("microservices"):
        os.makedirs("microservices")
    
    os.chdir("microservices")
    
    # Create missing services
    create_loyalty_service()
    create_ui_service()
    
    print("All missing services created successfully!")
    print("You can now run: docker-compose up")

if __name__ == "__main__":
    main()