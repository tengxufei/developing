import boto3
import os

def get_aws_client(service_name: str):
    """Creates an AWS client for a specified service."""
    return boto3.client(
        service_name,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )

def create_s3_bucket_if_not_exists(bucket_name: str, region: str):
    """
    Creates an S3 bucket if it doesn't already exist.
    """
    s3_client = get_aws_client("s3")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except s3_client.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print(f"Bucket '{bucket_name}' not found. Creating it now in region {region}.")
            if region == "us-east-1":
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            raise e

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    S3_BUCKET_NAME = "bma-bioinformatics-task-xufei"
    AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")

    create_s3_bucket_if_not_exists(S3_BUCKET_NAME, AWS_REGION)

def run_job_on_ec2(
    job_script_path: str,
    s3_bucket_name: str,
    instance_type: str,
    ami_id: str,
    iam_instance_profile_name: str,
    key_name: str,
    script_args: dict = None,
):
    """
    Runs a job script on a new EC2 instance and retrieves the results.
    """
    s3_client = get_aws_client("s3")
    ec2_client = get_aws_client("ec2")

    script_name = os.path.basename(job_script_path)
    s3_script_key = f"scripts/{script_name}"
    s3_output_key = f"outputs/{os.path.splitext(script_name)[0]}.zip"

    # Upload the job script to S3
    print(f"Uploading '{job_script_path}' to S3 at '{s3_script_key}'...")
    s3_client.upload_file(job_script_path, s3_bucket_name, s3_script_key)
    print("Upload complete.")

        # Build the argument string for the script
    arg_string = ""
    if script_args:
        for key, value in script_args.items():
            arg_string += f" --{key} {value}"

    # User data script to run on the EC2 instance
    user_data = f"""#!/bin/bash
set -ex

# Install dependencies
apt-get update
apt-get install -y python3-pip awscli zip
pip3 install pandas matplotlib seaborn boto3

# Create directories
mkdir -p /home/ubuntu/analysis_output

# Download the script from S3
aws s3 cp s3://{s3_bucket_name}/{s3_script_key} /home/ubuntu/{script_name}
chmod +x /home/ubuntu/{script_name}

# Run the script
python3 /home/ubuntu/{script_name}{arg_string}

# Package and upload the output
zip -r /home/ubuntu/results.zip /home/ubuntu/analysis_output
aws s3 cp /home/ubuntu/results.zip s3://{s3_bucket_name}/{s3_output_key}

# Terminate the instance
shutdown -h now
"""

    # Launch the EC2 instance
    print(f"Launching EC2 instance ({instance_type}, {ami_id})...")
    run_instances_response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        InstanceInitiatedShutdownBehavior="terminate",
        UserData=user_data,
        IamInstanceProfile={"Name": iam_instance_profile_name},
        KeyName=key_name,
    )
    instance_id = run_instances_response["Instances"][0]["InstanceId"]
    print(f"Instance '{instance_id}' launched.")

    # Wait for the instance to be running
    print("Waiting for instance to be running...")
    running_waiter = ec2_client.get_waiter("instance_running")
    running_waiter.wait(InstanceIds=[instance_id])
    print("Instance is running.")

    # Wait for the instance to terminate (which means the job is done)
    print("Waiting for instance to terminate...")
    terminated_waiter = ec2_client.get_waiter("instance_terminated")
    terminated_waiter.wait(
        InstanceIds=[instance_id],
        WaiterConfig={"Delay": 30, "MaxAttempts": 60},
    )
    print("Instance terminated.")

    # Download the output from S3
    output_file_path = f"output/{os.path.splitext(script_name)[0]}.zip"
    print(f"Downloading output from S3 to '{output_file_path}'...")
    s3_client.download_file(s3_bucket_name, s3_output_key, output_file_path)
    print("Download complete.")

    return output_file_path
