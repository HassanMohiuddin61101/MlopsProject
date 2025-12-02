"""
Model Comparison Script for CML
Compares new model with production model and generates CML report
"""
import os
import sys
import mlflow
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.mlflow_config import setup_mlflow
from models.registry import get_latest_model, list_model_versions

load_dotenv()

def compare_models():
    """
    Compare new model with production model
    Generate CML report
    """
    # Setup MLflow
    setup_mlflow()
    client = mlflow.tracking.MlflowClient()
    
    # Get production model
    production_model = get_latest_model("dqn_trend_model", stage="Production")
    
    # Get latest model from experiment
    experiment = mlflow.get_experiment_by_name("crypto_trend_prediction")
    if not experiment:
        print("⚠️  No experiment found")
        return
    
    # Get latest run
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["attributes.start_time DESC"],
        max_results=1
    )
    
    if not runs:
        print("⚠️  No runs found in experiment")
        return
    
    latest_run = runs[0]
    
    # Extract metrics
    latest_metrics = latest_run.data.metrics
    latest_params = latest_run.data.params
    
    # Compare with production (if exists)
    report_lines = [
        "# Model Comparison Report",
        "",
        "## Latest Model Metrics",
        ""
    ]
    
    # Add metrics table
    report_lines.append("| Metric | Value |")
    report_lines.append("|--------|-------|")
    for metric_name, metric_value in latest_metrics.items():
        if isinstance(metric_value, (int, float)):
            report_lines.append(f"| {metric_name} | {metric_value:.4f} |")
        else:
            report_lines.append(f"| {metric_name} | {metric_value} |")
    
    report_lines.append("")
    report_lines.append("## Model Parameters")
    report_lines.append("")
    report_lines.append("| Parameter | Value |")
    report_lines.append("|-----------|-------|")
    for param_name, param_value in latest_params.items():
        report_lines.append(f"| {param_name} | {param_value} |")
    
    report_lines.append("")
    report_lines.append("## Model Information")
    report_lines.append("")
    report_lines.append(f"- **Run ID**: {latest_run.info.run_id}")
    report_lines.append(f"- **Experiment**: {experiment.name}")
    report_lines.append(f"- **Status**: {latest_run.info.status}")
    
    if production_model:
        report_lines.append("")
        report_lines.append("## Production Model")
        report_lines.append("")
        report_lines.append(f"- **Model URI**: {production_model}")
        report_lines.append("- Production model found in registry")
    else:
        report_lines.append("")
        report_lines.append("## Production Model")
        report_lines.append("")
        report_lines.append("- ⚠️  No production model found in registry")
    
    # Write report
    report_content = "\n".join(report_lines)
    with open("cml_report.md", "w") as f:
        f.write(report_content)
    
    print("✅ CML report generated: cml_report.md")
    print("\n" + report_content)
    
    return report_content

if __name__ == "__main__":
    compare_models()

