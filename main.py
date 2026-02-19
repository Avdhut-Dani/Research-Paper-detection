from researcher_system.core.pipeline import run_pipeline
from researcher_system.core.config import PAPER_PATH
from researcher_system.core.gpu_manager import show_gpu
from researcher_system.reports.report_generator import generate

print("Starting script...", flush=True)
show_gpu()
print("GPU info shown. Running pipeline...", flush=True)
result=run_pipeline(PAPER_PATH)
print("Pipeline finished. Generating report...", flush=True)
generate(result)
print("Script finished.", flush=True)
