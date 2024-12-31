import boto3
from botocore.exceptions import ClientError
import json  # Added import for json

def create_public_s3_file(bucket_name: str, file_path: str, object_key: str) -> bool:
    """
    Creates an S3 bucket (if it doesn't exist), uploads a file, and makes it publicly accessible.

    Args:
        bucket_name: The name of the S3 bucket.
        file_path: The local path to the file to upload.
        object_key: The key (name) of the object in S3.

    Returns:
        True if successful, False otherwise.
    """

    s3_client = boto3.client('s3')

    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': 'us-east-1'
            }
        )

        print(f"Bucket {bucket_name} created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyExists':
            print(f"Bucket {bucket_name} already exists")
        else:
            print(f"Error creating bucket: {e}")
            return False

    # 2. Upload the file
    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        print(f"File {file_path} uploaded successfully as {object_key}")
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False

    # 3. Make the object public
    try:
        # Configure bucket policy to allow public access to the specific object
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadForGetBucketObjects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/{object_key}"
                }
            ]
        }

        # Apply the policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )

        # Disable public access block for this bucket
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )

        print(f"The file is now public at: https://{bucket_name}.s3.amazonaws.com/{object_key}")
        return True

    except ClientError as e:
        print(f"Error making the file public: {e}")
        return False

# Example usage
if __name__ == "__main__":
    bucket_name = "my-unique-bucket-123"  # Must be a globally unique name
    file_path = "./my_file.txt"          # Path to the local file
    object_key = "my_file.txt"           # Name it will have in S3

    create_public_s3_file(bucket_name, file_path, object_key)
