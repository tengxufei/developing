import os
from langchain_aws.chat_models.bedrock import ChatBedrock

class ReportGenerationAgent:
    def __init__(self):
        self.llm = ChatBedrock(
            model_id=os.environ.get("ANTHROPIC_MODEL"),
            region_name=os.environ.get("AWS_REGION"),
        )

    def generate_report(
        self,
        prompt: str,
        script_code: str,
        result_files: list[str],
        critique: str,
        interpretation: str,
    ) -> str:
        """
        Generates a comprehensive analysis report in Markdown format.
        """
        system_prompt = """
        You are a senior computational biologist and scientific writer. Your task is to generate a detailed, publication-quality analysis report in Markdown format.
        You will be given the user's original prompt, the Python script that was generated and executed, a list of the resulting output files, a scientific critique of the methods, and a biological interpretation of the results.

        The report MUST follow this structure:
        1.  **Analysis Overview:** Briefly describe the goal of the analysis based on the user's prompt.
        2.  **Methodology:**
            *   Describe the analysis steps taken.
            *   Include key snippets of the Python code that was executed. Use Markdown for code blocks. Focus on the parts that load data, perform the main calculation, and generate plots.
        3.  **Results:**
            *   List the output files that were generated (e.g., CSV tables, PDF plots).
            *   Briefly describe what each file contains.
        4.  **Automated Review and Interpretation:**
            *   Include the full scientific critique under a "Scientific Critique" sub-heading.
            *   Include the full biological interpretation under a "Biological Interpretation" sub-heading.
        
        The final output should be ONLY the complete Markdown report.
        """

        # Create a detailed prompt for the LLM
        input_prompt = f"""
        **Original User Prompt:**
        {prompt}

        **Executed Python Script:**
        ```python
        {script_code}
        ```

        **Generated Result Files:**
        {', '.join(result_files)}

        **Scientific Critique:**
        {critique}

        **Biological Interpretation:**
        {interpretation}
        """

        full_prompt = f"{system_prompt}\n\n{input_prompt}"

        response = self.llm.invoke(full_prompt)
        return response.content
