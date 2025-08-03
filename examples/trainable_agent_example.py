import asyncio
import boto3
from bedrock_bio.core.trainable_agent import TrainableAgent, FeedbackType
from bedrock_bio.core.learning_manager import LearningManager

async def main():
    # Initialize AWS Bedrock client
    bedrock = boto3.client('bedrock-runtime')
    
    # Initialize trainable agent and learning manager
    agent = TrainableAgent(bedrock)
    learning_manager = LearningManager()
    
    # Start a learning session
    session_id = learning_manager.start_session(
        focus_areas=["molecular_biology", "cell_signaling"],
        objectives=[
            "Understand T cell exhaustion mechanisms",
            "Learn about cytokine signaling pathways"
        ]
    )
    
    # Example 1: Basic query and feedback
    query = "Explain the role of PD-1 in T cell exhaustion"
    response = await agent.process_query(query)
    
    # Log interaction
    learning_manager.add_interaction(
        session_id,
        {
            "query": query,
            "response": response,
            "areas": ["molecular_biology", "immunology"]
        }
    )
    
    # Provide feedback
    feedback = {
        "correction": {
            "point": "PD-1 signaling also affects metabolic reprogramming",
            "reference": "DOI: 10.1016/j.immuni.2020..."
        }
    }
    
    learning_result = await agent.provide_feedback(
        session_id,
        feedback,
        FeedbackType.CORRECTION
    )
    
    # Log feedback
    learning_manager.add_feedback(
        session_id,
        {
            "type": "correction",
            "content": feedback,
            "areas": ["molecular_biology"],
            "confidence": 0.8
        }
    )
    
    # Example 2: Query with learned knowledge
    response = await agent.process_query(
        "How does PD-1 signaling affect T cell metabolism?",
        context={"previous_learning": True}
    )
    
    # Example 3: Check learning progress
    progress = await agent.review_learning_progress("molecular_biology")
    print("\nLearning Progress:")
    print(progress)
    
    # Get session progress
    session_progress = learning_manager.get_session_progress(session_id)
    print("\nSession Progress:")
    print(session_progress)
    
    # Get learning recommendations
    recommendations = learning_manager.get_learning_recommendations(session_id)
    print("\nRecommendations:")
    print(recommendations)

if __name__ == "__main__":
    asyncio.run(main())
