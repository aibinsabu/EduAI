import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quality_app.settings") # Wait, is it quality_app.settings or edu.settings?
# Project structure:
# d:\New folder (2)\project\edu\manage.py
# Quality app is inside edu. So settings is likely edu.settings
