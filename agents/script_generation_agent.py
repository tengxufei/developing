import os
from langchain_aws.chat_models.bedrock import ChatBedrock

class ScriptGenerationAgent:
    def __init__(self):
        self.llm = ChatBedrock(
            model_id=os.environ.get("ANTHROPIC_MODEL"),
            region_name=os.environ.get("AWS_REGION"),
        )

    def generate_r_script(self, prompt: str):
        """
        Streams an R script based on a natural language prompt.
        """
        system_prompt = """
        You are an expert Python programmer specializing in bioinformatics.
        Your task is to generate a complete, executable Python script based on the user's request.
        The script should be self-contained and include library loading, data loading, analysis, and saving results.
        The script will be executed in an environment where pandas, matplotlib, seaborn, and boto3 are already installed.
        
        Key requirements for the script:
        1.  Use the `argparse` library to handle command-line arguments.
        2.  The script MUST accept the following three arguments:
            *   `--s3-path`: The full S3 path to the input data file (e.g., 's3://bucket/data/file.csv.gz').
            *   `--genes`: A comma-separated string of gene symbols to be analyzed (e.g., 'EGFR,PTEN,IDH1').
            *   `--output-dir`: The local directory on the EC2 instance where all result files (CSVs, plots) must be saved.
        3.  The script should parse the `--genes` string into a list.
        4.  Use the `boto3` library to download the data from the specified `--s3-path`.
        5.  The final output should be ONLY the raw Python code, with no explanations, comments, or markdown formatting.
        """

        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        # Use the stream method to get chunks of code
        for chunk in self.llm.stream(full_prompt):
            yield chunk.content
