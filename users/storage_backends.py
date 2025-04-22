from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class MediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = "media"  # Subdirectory in the bucket
    file_overwrite = True  # Allow overwriting files
    default_acl = "public-read"  # Make files publicly readable

    # Don't use custom domain - let Django build the URLs
    custom_domain = None

    def exists(self, name):
        # Always return False to overwrite existing files
        return False

    def url(self, name, parameters=None, expire=None):
        """
        Return a direct URL to the object using the external MinIO URL
        """
        # Use simple direct URL format for direct access via nginx proxy
        if settings.DEBUG:
            # For local development, use the media URL directly
            return f"{settings.MEDIA_URL}{name}"
        else:
            # For production, construct URL via MinIO accessible URL
            # The /media/ part is handled by nginx proxy
            return f"/media/{name}"
