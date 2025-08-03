from typing import Dict, List, Any, Optional
import datetime
from dataclasses import dataclass
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class LearningSession:
    session_id: str
    start_time: datetime.datetime
    focus_areas: List[str]
    objectives: List[str]
    interactions: List[Dict] = None
    feedback_history: List[Dict] = None
    
class LearningManager:
    """
    Manages the learning process for the trainable agent
    """
    
    def __init__(self):
        self.sessions = {}
        self.vectorizer = TfidfVectorizer()
        self.knowledge_vectors = {}
        self.learning_metrics = {}
        
    def start_session(self,
                     focus_areas: List[str],
                     objectives: List[str]) -> str:
        """Start a new learning session"""
        session_id = self._generate_session_id()
        
        session = LearningSession(
            session_id=session_id,
            start_time=datetime.datetime.now(),
            focus_areas=focus_areas,
            objectives=objectives,
            interactions=[],
            feedback_history=[]
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def add_interaction(self,
                       session_id: str,
                       interaction: Dict[str, Any]):
        """Add an interaction to the session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        session.interactions.append({
            "timestamp": datetime.datetime.now(),
            **interaction
        })
        
        # Update knowledge vectors
        self._update_knowledge_vectors(interaction)
    
    def add_feedback(self,
                    session_id: str,
                    feedback: Dict[str, Any]):
        """Add feedback to the session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        session.feedback_history.append({
            "timestamp": datetime.datetime.now(),
            **feedback
        })
        
        # Update learning metrics
        self._update_learning_metrics(session_id, feedback)
    
    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress of a learning session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        
        return {
            "duration": (datetime.datetime.now() - session.start_time).total_seconds(),
            "interactions": len(session.interactions),
            "feedback_count": len(session.feedback_history),
            "objectives_progress": self._evaluate_objectives_progress(session),
            "knowledge_growth": self._measure_knowledge_growth(session),
            "confidence_trend": self._analyze_confidence_trend(session)
        }
    
    def get_learning_recommendations(self,
                                  session_id: str) -> List[Dict[str, Any]]:
        """Get recommendations for improving learning"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        
        # Analyze current state
        progress = self.get_session_progress(session_id)
        
        # Generate recommendations
        recommendations = []
        
        # Check objective progress
        for obj, prog in progress["objectives_progress"].items():
            if prog < 0.7:  # Less than 70% progress
                recommendations.append({
                    "type": "objective_focus",
                    "objective": obj,
                    "suggestion": f"Focus more on understanding {obj}",
                    "priority": "high"
                })
        
        # Check knowledge gaps
        gaps = self._identify_knowledge_gaps(session)
        for gap in gaps:
            recommendations.append({
                "type": "knowledge_gap",
                "area": gap["area"],
                "suggestion": f"Explore more about {gap['topic']}",
                "priority": "medium"
            })
        
        # Check interaction patterns
        if self._needs_more_diverse_interactions(session):
            recommendations.append({
                "type": "interaction_diversity",
                "suggestion": "Try different types of questions and scenarios",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _update_knowledge_vectors(self, interaction: Dict[str, Any]):
        """Update knowledge vectors based on interaction"""
        text = f"{interaction['query']} {json.dumps(interaction['response'])}"
        vector = self.vectorizer.fit_transform([text])
        
        for area in interaction.get("areas", []):
            if area not in self.knowledge_vectors:
                self.knowledge_vectors[area] = vector
            else:
                self.knowledge_vectors[area] += vector
    
    def _update_learning_metrics(self,
                               session_id: str,
                               feedback: Dict[str, Any]):
        """Update learning metrics based on feedback"""
        if session_id not in self.learning_metrics:
            self.learning_metrics[session_id] = {
                "feedback_count": 0,
                "positive_feedback": 0,
                "areas_improved": set(),
                "confidence_scores": []
            }
        
        metrics = self.learning_metrics[session_id]
        metrics["feedback_count"] += 1
        
        if feedback.get("type") == "positive":
            metrics["positive_feedback"] += 1
        
        if "areas" in feedback:
            metrics["areas_improved"].update(feedback["areas"])
        
        if "confidence" in feedback:
            metrics["confidence_scores"].append(feedback["confidence"])
    
    def _evaluate_objectives_progress(self,
                                   session: LearningSession) -> Dict[str, float]:
        """Evaluate progress towards session objectives"""
        progress = {}
        
        for objective in session.objectives:
            # Calculate progress based on interactions and feedback
            relevant_interactions = [
                i for i in session.interactions
                if self._is_relevant_to_objective(i, objective)
            ]
            
            if not relevant_interactions:
                progress[objective] = 0.0
                continue
            
            # Calculate progress score
            scores = []
            for interaction in relevant_interactions:
                score = self._calculate_interaction_score(interaction)
                scores.append(score)
            
            progress[objective] = np.mean(scores)
        
        return progress
    
    def _measure_knowledge_growth(self,
                                session: LearningSession) -> Dict[str, float]:
        """Measure knowledge growth in different areas"""
        growth = {}
        
        for area in session.focus_areas:
            if area not in self.knowledge_vectors:
                growth[area] = 0.0
                continue
            
            # Calculate knowledge growth using vector similarity
            initial_vector = self.knowledge_vectors[area]
            current_vector = self._calculate_current_knowledge_vector(session, area)
            
            similarity = cosine_similarity(initial_vector, current_vector)[0][0]
            growth[area] = max(0, similarity - 1)  # Growth is increase in similarity
        
        return growth
    
    def _analyze_confidence_trend(self,
                                session: LearningSession) -> Dict[str, Any]:
        """Analyze trend in confidence scores"""
        if session.session_id not in self.learning_metrics:
            return {"trend": "unknown"}
        
        scores = self.learning_metrics[session.session_id]["confidence_scores"]
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        trend = np.polyfit(range(len(scores)), scores, 1)[0]
        
        return {
            "trend": "improving" if trend > 0 else "declining",
            "trend_value": float(trend),
            "current_confidence": scores[-1]
        }
    
    def _identify_knowledge_gaps(self,
                               session: LearningSession) -> List[Dict[str, Any]]:
        """Identify gaps in knowledge"""
        gaps = []
        
        for area in session.focus_areas:
            # Analyze interactions in this area
            area_interactions = [
                i for i in session.interactions
                if area in i.get("areas", [])
            ]
            
            # Identify topics with low confidence or negative feedback
            topics = self._extract_topics(area_interactions)
            for topic, metrics in topics.items():
                if metrics["confidence"] < 0.7 or metrics["negative_feedback"] > 0:
                    gaps.append({
                        "area": area,
                        "topic": topic,
                        "confidence": metrics["confidence"],
                        "negative_feedback": metrics["negative_feedback"]
                    })
        
        return gaps
    
    def _needs_more_diverse_interactions(self,
                                      session: LearningSession) -> bool:
        """Check if interactions need more diversity"""
        if len(session.interactions) < 5:
            return False
            
        # Analyze interaction types
        types = [i.get("type") for i in session.interactions[-5:]]
        unique_types = len(set(types))
        
        return unique_types < 3  # Need at least 3 different types
    
    def _is_relevant_to_objective(self,
                                interaction: Dict[str, Any],
                                objective: str) -> bool:
        """Check if interaction is relevant to objective"""
        # Implement relevance checking logic
        return True
    
    def _calculate_interaction_score(self,
                                  interaction: Dict[str, Any]) -> float:
        """Calculate score for an interaction"""
        # Implement scoring logic
        return 0.5
    
    def _calculate_current_knowledge_vector(self,
                                         session: LearningSession,
                                         area: str):
        """Calculate current knowledge vector for area"""
        # Implement vector calculation
        return self.knowledge_vectors[area]
    
    def _extract_topics(self,
                       interactions: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Extract topics and their metrics from interactions"""
        # Implement topic extraction
        return {}
