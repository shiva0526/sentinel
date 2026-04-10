import traceback
from agents.report_agent import run_report_agent
try:
    print("Testing report agent directly:")
    run_report_agent([], [])
    print("Success!")
except Exception as e:
    print("Failed!")
    traceback.print_exc()
