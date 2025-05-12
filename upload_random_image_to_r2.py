import os
import random
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# --- Configuration ---
LOCAL_PHOTO_DIRECTORY = "/path/to/your/machine/photos/folder"  # Replace with your photo folder
R2_BUCKET_NAME = "your-r2-bucket-name"  # Replace with your R2 bucket name
R2_PHOTO_KEY = "current-display-photo.jpg"  # Keep this as it is. 

R2_ACCOUNT_ID = "YOUR_R2_ACCOUNT_ID"
R2_ACCESS_KEY_ID = "YOUR_R2_ACCESS_KEY_ID"
R2_SECRET_ACCESS_KEY = "YOUR_R2_SECRET_ACCESS_KEY"

R2_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

def get_random_photo(directory):
    """Selects a random photo from the specified directory."""
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return None
    
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    photos = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(allowed_extensions)
    ]
    if not photos:
        print(f"No photos found in '{directory}'.")
        return None
    return random.choice(photos)

def upload_to_r2(file_path, bucket_name, object_key):
    """Uploads a file to Cloudflare R2."""
    s3_client = boto3.client(
        service_name='s3',
        endpoint_url=R2_ENDPOINT_URL,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto',  # Or your specific region if configured
    )
    try:
        print(f"Uploading '{file_path}' to R2 bucket '{bucket_name}' as '{object_key}'...")
        s3_client.upload_file(
            file_path,
            bucket_name,
            object_key,
            ExtraArgs={'ContentType': 'image/jpeg'} # Adjust based on your typical image type
        )
        print("Upload successful!")
        return True
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return False
    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        return False
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
        return False
    except ClientError as e:
        print(f"ClientError uploading to R2: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during upload: {e}")
        return False

if __name__ == "__main__":
    print("Starting photo selection and upload process...")
    random_photo_path = get_random_photo(LOCAL_PHOTO_DIRECTORY)

    if random_photo_path:
        if upload_to_r2(random_photo_path, R2_BUCKET_NAME, R2_PHOTO_KEY):
            print(f"Successfully uploaded '{random_photo_path}' as '{R2_PHOTO_KEY}' in bucket '{R2_BUCKET_NAME}'.")
        else:
            print("Failed to upload the photo.")
    else:
        print("No photo selected to upload.")
    print("Process finished.")
