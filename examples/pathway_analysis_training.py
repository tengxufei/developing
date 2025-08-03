import asyncio
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from typing import Dict, List, Any

class PathwayAnalysisTrainer:
    """
    Demonstrates trainable analysis of pathway data with real statistical methods
    """
    
    def __init__(self):
        # Initialize with simulated pathway expression data
        self.generate_training_data()
        self.knowledge = {
            "statistical_tests": [],
            "correlations": [],
            "pathway_insights": []
        }
        self.performance_history = []
        
    def generate_training_data(self):
        """Generate realistic pathway expression data"""
        np.random.seed(42)
        n_samples = 100
        
        # Generate correlated expression data for pathway components
        self.true_correlations = np.array([
            [1.0, 0.7, 0.4],
            [0.7, 1.0, 0.8],
            [0.4, 0.8, 1.0]
        ])
        
        # Generate expression data with known relationships
        self.expression_data = pd.DataFrame(
            np.random.multivariate_normal(
                mean=[10, 8, 12],
                cov=self.true_correlations,
                size=n_samples
            ),
            columns=['RAF', 'MEK', 'ERK']
        )
        
        # Add some noise
        self.expression_data += np.random.normal(0, 0.5, self.expression_data.shape)
        
        # Generate condition labels
        self.conditions = np.array(['control'] * (n_samples//2) + ['treated'] * (n_samples//2))
        
        # Add treatment effect
        treatment_effect = np.array([1.5, 2.0, 2.5])
        self.expression_data.loc[self.conditions == 'treated'] += treatment_effect
        
    async def train_step(self, step_type: str) -> Dict[str, Any]:
        """Perform a training step of specified type"""
        if step_type == "correlation":
            return await self._train_correlation()
        elif step_type == "differential":
            return await self._train_differential()
        elif step_type == "pathway":
            return await self._train_pathway_analysis()
        else:
            raise ValueError(f"Unknown training step type: {step_type}")
    
    async def _train_correlation(self) -> Dict[str, Any]:
        """Train on correlation analysis"""
        # Current knowledge check
        current_correlations = len(self.knowledge["correlations"])
        
        # Calculate actual correlations
        calculated_corr = self.expression_data.corr()
        
        # Determine what to learn next
        if current_correlations == 0:
            # Learn RAF-MEK correlation
            new_correlation = {
                "pair": ("RAF", "MEK"),
                "correlation": calculated_corr.loc["RAF", "MEK"],
                "p_value": self._calculate_correlation_pvalue("RAF", "MEK")
            }
        elif current_correlations == 1:
            # Learn MEK-ERK correlation
            new_correlation = {
                "pair": ("MEK", "ERK"),
                "correlation": calculated_corr.loc["MEK", "ERK"],
                "p_value": self._calculate_correlation_pvalue("MEK", "ERK")
            }
        else:
            # Learn RAF-ERK correlation
            new_correlation = {
                "pair": ("RAF", "ERK"),
                "correlation": calculated_corr.loc["RAF", "ERK"],
                "p_value": self._calculate_correlation_pvalue("RAF", "ERK")
            }
        
        # Update knowledge
        self.knowledge["correlations"].append(new_correlation)
        
        # Calculate performance
        performance = len(self.knowledge["correlations"]) / 3
        self.performance_history.append(performance)
        
        return {
            "step_type": "correlation",
            "learned": new_correlation,
            "performance": performance,
            "feedback": self._generate_correlation_feedback(new_correlation)
        }
    
    async def _train_differential(self) -> Dict[str, Any]:
        """Train on differential expression analysis"""
        # Current knowledge check
        current_tests = len(self.knowledge["statistical_tests"])
        
        # Perform t-test for each gene
        genes = ['RAF', 'MEK', 'ERK']
        if current_tests >= len(genes):
            return {"status": "completed"}
        
        gene = genes[current_tests]
        control = self.expression_data[gene][self.conditions == 'control']
        treated = self.expression_data[gene][self.conditions == 'treated']
        
        t_stat, p_value = stats.ttest_ind(control, treated)
        fold_change = treated.mean() / control.mean()
        
        result = {
            "gene": gene,
            "t_statistic": t_stat,
            "p_value": p_value,
            "fold_change": fold_change
        }
        
        # Update knowledge
        self.knowledge["statistical_tests"].append(result)
        
        # Calculate performance
        performance = len(self.knowledge["statistical_tests"]) / len(genes)
        self.performance_history.append(performance)
        
        return {
            "step_type": "differential",
            "learned": result,
            "performance": performance,
            "feedback": self._generate_differential_feedback(result)
        }
    
    async def _train_pathway_analysis(self) -> Dict[str, Any]:
        """Train on pathway-level analysis"""
        current_insights = len(self.knowledge["pathway_insights"])
        
        if current_insights == 0:
            # Learn about pathway structure
            insight = {
                "type": "structure",
                "content": "RAF phosphorylates MEK, which phosphorylates ERK"
            }
        elif current_insights == 1:
            # Learn about pathway regulation
            insight = {
                "type": "regulation",
                "content": "Treatment increases activity across the pathway"
            }
        else:
            # Learn about feedback mechanisms
            insight = {
                "type": "feedback",
                "content": "ERK can provide negative feedback to RAF"
            }
        
        # Update knowledge
        self.knowledge["pathway_insights"].append(insight)
        
        # Calculate performance
        performance = len(self.knowledge["pathway_insights"]) / 3
        self.performance_history.append(performance)
        
        return {
            "step_type": "pathway",
            "learned": insight,
            "performance": performance,
            "feedback": self._generate_pathway_feedback(insight)
        }
    
    def _calculate_correlation_pvalue(self, gene1: str, gene2: str) -> float:
        """Calculate p-value for correlation between two genes"""
        corr, p_value = stats.pearsonr(
            self.expression_data[gene1],
            self.expression_data[gene2]
        )
        return p_value
    
    def _generate_correlation_feedback(self, correlation: Dict) -> str:
        """Generate feedback for correlation analysis"""
        gene1, gene2 = correlation["pair"]
        corr = correlation["correlation"]
        if abs(corr) > 0.7:
            return f"Strong correlation ({corr:.2f}) found between {gene1} and {gene2}"
        else:
            return f"Moderate correlation ({corr:.2f}) found between {gene1} and {gene2}"
    
    def _generate_differential_feedback(self, result: Dict) -> str:
        """Generate feedback for differential expression analysis"""
        if result["p_value"] < 0.05:
            return f"{result['gene']} is significantly different between conditions (FC={result['fold_change']:.2f})"
        else:
            return f"{result['gene']} shows no significant difference between conditions"
    
    def _generate_pathway_feedback(self, insight: Dict) -> str:
        """Generate feedback for pathway insight"""
        return f"New pathway insight learned: {insight['content']}"
    
    def plot_learning_curves(self):
        """Plot learning curves for different aspects"""
        plt.figure(figsize=(15, 5))
        
        # Plot correlation learning
        plt.subplot(131)
        corr_progress = [i/3 for i in range(len(self.knowledge["correlations"]))]
        plt.plot(corr_progress, 'b-', marker='o', label='Correlations')
        plt.title('Correlation Analysis Learning')
        plt.xlabel('Step')
        plt.ylabel('Progress')
        
        # Plot differential expression learning
        plt.subplot(132)
        diff_progress = [i/3 for i in range(len(self.knowledge["statistical_tests"]))]
        plt.plot(diff_progress, 'r-', marker='o', label='Differential Expression')
        plt.title('Differential Expression Learning')
        plt.xlabel('Step')
        
        # Plot pathway insight learning
        plt.subplot(133)
        pathway_progress = [i/3 for i in range(len(self.knowledge["pathway_insights"]))]
        plt.plot(pathway_progress, 'g-', marker='o', label='Pathway Insights')
        plt.title('Pathway Understanding')
        plt.xlabel('Step')
        
        plt.tight_layout()
        plt.savefig('pathway_learning_curves.png')
        plt.close()

async def demonstrate_pathway_training():
    # Initialize trainer
    trainer = PathwayAnalysisTrainer()
    
    print("Starting pathway analysis training demonstration...")
    
    # Train correlation analysis
    print("\nLearning Correlations:")
    for _ in range(3):
        result = await trainer.train_step("correlation")
        print(f"Step result: {result['feedback']}")
    
    # Train differential expression
    print("\nLearning Differential Expression:")
    for _ in range(3):
        result = await trainer.train_step("differential")
        print(f"Step result: {result['feedback']}")
    
    # Train pathway analysis
    print("\nLearning Pathway Insights:")
    for _ in range(3):
        result = await trainer.train_step("pathway")
        print(f"Step result: {result['feedback']}")
    
    # Plot learning curves
    trainer.plot_learning_curves()
    print("\nLearning curves have been saved as 'pathway_learning_curves.png'")

if __name__ == "__main__":
    asyncio.run(demonstrate_pathway_training())
