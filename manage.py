import os

# MUST be before any mediapipe / tensorflow / cv2 import
os.environ["GLOG_minloglevel"] = "3"
os.environ["GLOG_stderrthreshold"] = "3"
os.environ["GLOG_logtostderr"] = "0"
os.environ["GLOG_v"] = "0"
os.environ["ABSL_MIN_LOG_LEVEL"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"

from django.core.management import execute_from_command_line

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
