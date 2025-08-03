import boto3
import json
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

class CustomBedrockClient:
    def __init__(self, region_name="ap-southeast-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    def invoke_model(self, prompt):
        # Properly format the prompt for the JSON body
        prompt_json = json.dumps(prompt)
        
        # Updated body structure for Claude 3
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        })

        try:
            response = self.client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=body,
            )
            
            # Read the streaming body and parse the JSON response
            response_body = json.loads(response.get("body").read())
            
            # Extract the generated text content
            return response_body['content'][0]['text']

        except Exception as e:
            print(f"ERROR: An error occurred while invoking the Bedrock model: {e}")
            return f"Error in model invocation: {e}"

def get_langchain_bedrock_llm(model_id: str = "anthropic.claude-3-haiku-20240307-v1:0", region_name: str = "ap-southeast-1"):
    """
    Returns a Langchain Bedrock Chat model instance.
    """
    llm = ChatBedrock(
        model_id=model_id,
        region_name=region_name,
        model_kwargs={"temperature": 0.1, "max_tokens": 4096}
    )
    return llm
