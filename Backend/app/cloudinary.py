import cloudinary
import cloudinary.uploader

from app.config import settings


cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


def upload_image(file):
    result = cloudinary.uploader.upload(file)

    return result.get("secure_url")

def upload_video(file):
    result = cloudinary.uploader.upload(
        file,
        resource_type="video"
    )

    return result.get("secure_url")

def upload_file(file, resource_type="auto"):

    result = cloudinary.uploader.upload(
        file,
        resource_type=resource_type
    )

    return {
        "url": result.get("secure_url"),
        "type": result.get("resource_type"),
        "name": result.get("original_filename"),
        "size": result.get("bytes")
    }