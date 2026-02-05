import os
import django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File

# Initialize Django environment
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def migrate_media_to_r2():
    """
    Traverse the local media directory and upload all files to the configured
    default storage (R2).
    """
    media_root = settings.MEDIA_ROOT
    print(f"Starting migration from {media_root} to Cloudflare R2...")

    for root, dirs, files in os.walk(media_root):
        for file in files:
            local_path = os.path.join(root, file)
            # Get relative path for storage
            relative_path = os.path.relpath(local_path, media_root)
            # Standardize path separators for S3/R2
            relative_path = relative_path.replace('\\', '/')

            if not default_storage.exists(relative_path):
                print(f"Uploading: {relative_path}")
                try:
                    with open(local_path, 'rb') as f:
                        default_storage.save(relative_path, File(f))
                    print(f"Successfully uploaded: {relative_path}")
                except Exception as e:
                    print(f"Failed to upload {relative_path}: {e}")
            else:
                print(f"Skipping: {relative_path} (already exists)")

    print("Migration completed!")

if __name__ == "__main__":
    migrate_media_to_r2()
