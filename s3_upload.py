import boto3


def upload_inventory():

    # AWS Session
    session = boto3.Session(profile_name="aws-project")
    s3 = session.client("s3")

    # S3 Configuration
    bucket_name = "talha-aws-automation-inventory-2026"
    file_name = "inventory.json"

    # Upload Inventory
    s3.upload_file(
        file_name,
        bucket_name,
        file_name
    )

    print("Inventory uploaded to S3 successfully.")