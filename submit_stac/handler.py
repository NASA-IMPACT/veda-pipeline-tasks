from dataclasses import dataclass
import json
import os
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, TypedDict, Union

import boto3
import requests


class InputBase(TypedDict):
    dry_run: Optional[Any]


class S3LinkInput(InputBase):
    stac_file_url: str
    s3uri: str
    citations: Optional[List[str]]


class StacItemInput(InputBase):
    stac_item: Dict[str, Any]
    s3uri: str
    citations: Optional[List[str]]


class AppConfig(TypedDict):
    cognito_domain: str
    client_id: str
    client_secret: str
    scope: str


class Creds(TypedDict):
    access_token: str
    expires_in: int
    token_type: str


@dataclass
class IngestionApi:
    base_url: str
    token: str
    blockchain_base_url: str

    @classmethod
    def from_veda_auth_secret(
        cls, *, secret_id: str, base_url: str, blockchain_base_url: str
    ) -> "IngestionApi":
        cognito_details = cls._get_cognito_service_details(secret_id)
        credentials = cls._get_app_credentials(**cognito_details)
        return cls(
            token=credentials["access_token"],
            base_url=base_url,
            blockchain_base_url=blockchain_base_url,
        )

    @staticmethod
    def _get_cognito_service_details(secret_id: str) -> AppConfig:
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])

    @staticmethod
    def _get_app_credentials(
        cognito_domain: str, client_id: str, client_secret: str, scope: str, **kwargs
    ) -> Creds:
        response = requests.post(
            f"{cognito_domain}/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            auth=(client_id, client_secret),
            data={
                "grant_type": "client_credentials",
                # A space-separated list of scopes to request for the generated access token.
                "scope": scope,
            },
        )
        try:
            response.raise_for_status()
        except:
            print(response.text)
            raise
        return response.json()

    def submit(self, url: str, body: Dict[str, Any]):
        response = requests.post(
            url=url,
            json=body,
            headers={"Authorization": f"bearer {self.token}"},
        )

        try:
            response.raise_for_status()
        except Exception as e:
            print(response.text)
            raise e

        return response.json()

    def submit_to_ingestor(self, stac_item: Dict[str, Any]):
        self.submit(
            url=f"{self.base_url.rstrip('/')}/ingestions",
            body=stac_item,
        )

    def submit_to_blockchain(self, metadata: Dict[str, Any]):
        self.submit(
            url=f"{self.blockchain_url.rstrip('/')}/metadata/s3",
            body=metadata,
        )


def get_stac_item(event: Dict[str, Any]) -> Dict[str, Any]:
    if stac_item := event.get("stac_item"):
        return stac_item

    if file_url := event.get("stac_file_url"):
        url = urlparse(file_url)

        response = boto3.client("s3").get_object(
            Bucket=url.hostname,
            Key=url.path.lstrip("/"),
        )
        return json.load(response["Body"])

    raise Exception("No stac_item or stac_file_url provided")


def submission_handler(event: Union[S3LinkInput, StacItemInput], context) -> None:
    stac_item = get_stac_item(event)

    if event.get("dry_run"):
        print("Dry run, not inserting, would have inserted:")
        print(json.dumps(stac_item, indent=2))
        return

    ingestor = IngestionApi.from_veda_auth_secret(
        secret_id=os.environ["COGNITO_APP_SECRET"],
        base_url=os.environ["STAC_INGESTOR_API_URL"],
        blockchain_base_url=os.environ["STAC_INGESTOR_API_URL"],
    )
    ingestor.submit_to_ingestor(stac_item)
    # print("Successfully submitted STAC item")

    s3uri = event.get("s3uri")
    name = s3uri.split("/")[-1]
    # Prep blockchain payload
    payload = {
        "name": name,
        "s3uri": s3uri,
        "username": "",
        "citations": event.get("citations"),
    }
    ingestor.submit_to_blockchain(payload)


if __name__ == "__main__":
    filename = "example.ndjson"
    sample_event = {
        "s3uri": "s3://bucket/key",
        "citations": ["metadata1id"],
        "stac_file_url": "example.ndjson",
        # or
        "stac_item": {},
    }
    submission_handler(sample_event, {})
