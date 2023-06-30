import os
from s3_discovery import s3_discovery
import boto3


def assume_role(role_arn, session_name="veda-data-pipelines_s3-discovery"):
    sts = boto3.client("sts")
    credentials = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name,
    )
    creds = credentials["Credentials"]
    return {
        "aws_access_key_id": creds["AccessKeyId"],
        "aws_secret_access_key": creds.get("SecretAccessKey"),
        "aws_session_token": creds.get("SessionToken"),
    }

def s3_discovery_handler(event, chunk_size=2800, role_arn=None, bucket_output=None):
    
    role_arn = os.environ.get("ASSUME_ROLE_ARN", role_arn)
    kwargs = assume_role(role_arn=role_arn) if role_arn else {}
    out_keys, discovered = s3_discovery(event, chunk_size, bucket_output, kwargs)

    return {**event, "payload": out_keys, "discovered": discovered}
