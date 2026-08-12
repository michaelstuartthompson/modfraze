#!/usr/bin/env python3
"""
Quick setup script for viral merch pipeline.
Run this after installing requirements to verify everything works.
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False


def check_env_var(var_name, optional=False):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value:
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"✅ {var_name}: {masked}")
        return True
    else:
        status = "⚠️  OPTIONAL" if optional else "❌ REQUIRED"
        print(f"{status} {var_name}: Not set")
        return optional


def main():
    print("\n" + "="*60)
    print("🚀 VIRAL MERCH PIPELINE - SETUP CHECK")
    print("="*60 + "\n")
    
    # Check Python version
    print("📋 Python Version:")
    py_version = sys.version_info
    if py_version.major >= 3 and py_version.minor >= 9:
        print(f"✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        print(f"❌ Python {py_version.major}.{py_version.minor} (3.9+ required)")
        return False
    
    print("\n📁 Project Structure:")
    checks = [
        ("db/models.py", "Database models"),
        ("tools/dalle_client.py", "DALL-E client"),
        ("tools/shopify_client.py", "Shopify client"),
        ("pipeline/generate_designs.py", "Design pipeline"),
        ("ui/approval_dashboard.py", "Streamlit UI"),
        ("workflows/prefect_flows.py", "Prefect workflows"),
    ]
    
    all_good = True
    for filepath, desc in checks:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    print("\n🔑 Environment Variables:")
    
    # Load .env if exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  .env file not found (copy from .env.example)")
        all_good = False
    
    # Check critical environment variables
    print("\nCritical Variables:")
    critical = [
        "OPENAI_API_KEY",
        "APIFY_API_KEY",
        "SHOPIFY_SHOP_NAME",
        "SHOPIFY_ACCESS_TOKEN",
    ]
    
    for var in critical:
        if not check_env_var(var, optional=False):
            all_good = False
    
    print("\nOptional Variables:")
    optional = [
        "PRINTIFY_API_KEY",
        "META_ACCESS_TOKEN",
        "SENDGRID_API_KEY",
        "SLACK_WEBHOOK_URL",
    ]
    
    for var in optional:
        check_env_var(var, optional=True)
    
    print("\n📦 Python Packages:")
    try:
        import sqlalchemy
        print("✅ SQLAlchemy")
    except ImportError:
        print("❌ SQLAlchemy - run: pip install -r requirements.txt")
        all_good = False
    
    try:
        import prefect
        print("✅ Prefect")
    except ImportError:
        print("❌ Prefect - run: pip install -r requirements.txt")
        all_good = False
    
    try:
        import streamlit
        print("✅ Streamlit")
    except ImportError:
        print("❌ Streamlit - run: pip install -r requirements.txt")
        all_good = False
    
    try:
        import openai
        print("✅ OpenAI")
    except ImportError:
        print("❌ OpenAI - run: pip install -r requirements.txt")
        all_good = False
    
    print("\n" + "="*60)
    
    if all_good:
        print("✅ SETUP COMPLETE - Ready to go!")
        print("\nNext steps:")
        print("  1. Initialize database: python db/database.py")
        print("  2. Test trend scraping: python pipeline/ingest_tiktok.py")
        print("  3. Start approval UI: streamlit run ui/approval_dashboard.py")
        print("  4. Run workflows: python workflows/prefect_flows.py run daily")
    else:
        print("⚠️  SETUP INCOMPLETE - See errors above")
        print("\nFix issues and run: python setup_check.py")
    
    print("="*60 + "\n")
    
    return all_good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
