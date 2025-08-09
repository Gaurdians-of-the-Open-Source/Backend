import os

def check_analysis_status(project_id: str) -> str:
    static_json_path = f"results/{project_id}/static.json"
    llm_json_path = f"results/{project_id}/llm.json"
    pdf_report_path = f"reports/{project_id}.pdf"
    error_file_path = f"results/{project_id}/error.json"

    if os.path.exists(pdf_report_path):
        return "done"

    if os.path.exists(error_file_path):
        return "error"

    if os.path.exists(static_json_path) and os.path.exists(llm_json_path):
        return "pending"
    
    return "pending"