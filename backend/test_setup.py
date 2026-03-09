"""
Quick test script to verify Flask setup
"""
from app import create_app

if __name__ == '__main__':
    try:
        app = create_app()
        print('✓ Flask app created successfully!')
        print(f'✓ App name: {app.config["APP_NAME"]}')
        print(f'✓ Debug mode: {app.config["DEBUG"]}')
        print(f'✓ Database URI configured: {"postgresql" in app.config["SQLALCHEMY_DATABASE_URI"]}')
        print('\n✓ Phase 0 setup successful! Ready to proceed to Phase 1.')
    except Exception as e:
        print(f'✗ Error creating app: {e}')
