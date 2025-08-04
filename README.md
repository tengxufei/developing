# Bioinformatics Analysis System

This system combines automated execution with collaborative planning to tackle complex biological questions.

It operates in two phases:

1.  **Collaborative Planning:** Its agents act as a team of consultants that discuss and design a plan to tackle a biological question. The primary output is the refined plan itself, including the debate and reasoning.

2.  **Automated Execution:** It takes a high-level bioinformatics task, breaks it down using an orchestrator, and uses agents and cloud resources (boto3, EC2 scripts) to actually perform the analysis and generate concrete output files (plots, reports, data).

This dual approach ensures that the analysis is not only scientifically sound, thanks to the collaborative planning phase, but also efficiently executed to produce tangible results.