import asyncio
from bedrock_bio import AgentCoordinator

async def main():
    # Initialize coordinator
    coordinator = AgentCoordinator(
        region_name="us-east-1"  # or your preferred region
    )
    
    # Example 1: Process a biological query
    query_response = await coordinator.process_query(
        "What are the key regulators of T cell exhaustion?"
    )
    print("\nQuery Response:")
    print(query_response)
    
    # Example 2: Analyze scRNA-seq data
    analysis_response = await coordinator.analyze_dataset(
        data_path="/path/to/your/data.h5ad",
        analysis_type="scRNA-seq"
    )
    print("\nAnalysis Response:")
    print(analysis_response)

if __name__ == "__main__":
    asyncio.run(main())
