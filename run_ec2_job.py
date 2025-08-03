from orchestrator.aws_utils import run_job_on_ec2
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()

    S3_BUCKET_NAME = "bma-bioinformatics-task-xufei"
    INSTANCE_TYPE = "t3.small"
    AMI_ID = "ami-04056160f0fcaaf17"  # Ubuntu 22.04 LTS in ap-southeast-1
    IAM_INSTANCE_PROFILE_NAME = "BMA-EC2-Instance-Profile"
    JOB_SCRIPT_PATH = "sample_job.py"
    KEY_NAME = "agentic_test"

    output_file = run_job_on_ec2(
        job_script_path=JOB_SCRIPT_PATH,
        s3_bucket_name=S3_BUCKET_NAME,
        instance_type=INSTANCE_TYPE,
        ami_id=AMI_ID,
        iam_instance_profile_name=IAM_INSTANCE_PROFILE_NAME,
        key_name=KEY_NAME,
    )

    print(f"Job finished. Output written to: {output_file}")
    with open(output_file, "r") as f:
        print("Output file content:")
        print(f.read())
