from typing import List
import boto3
import json

class Embeddings:
    def __init__(self, region, model_id):
        self.model_id = model_id
        self.bedrock_client = boto3.client("bedrock-runtime", region_name=region)

    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using the database's embed_text method.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({"inputText": text, "dimensions": 512}),
                accept="application/json",
                contentType="application/json",
            )
            body = json.loads(response["body"].read())
            embeddings = body['embedding']
            return embeddings
        except Exception as e:
            raise