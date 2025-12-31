import os
import django
import sys

# Add project root to path
sys.path.append(r'd:\New folder (2)\project\edu')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')

try:
    django.setup()
    from quality_app import views
    if hasattr(views, 'edit_user'):
        print("SUCCESS: edit_user found in views.")
    else:
        print("FAILURE: edit_user NOT found in views.")
        print(f"Views file: {views.__file__}")
        print("Dir(views):", dir(views))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
