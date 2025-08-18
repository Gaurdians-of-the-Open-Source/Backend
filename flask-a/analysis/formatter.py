import os
import json

def get_line_content(file_path, line_number):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[line_number - 1].strip() if 0 < line_number <= len(lines) else ""
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="ISO-8859-1") as f:
                lines = f.readlines()
            return lines[line_number - 1].strip() if 0 < line_number <= len(lines) else ""
        except Exception as e:
            print(f"[Latin-1 디코딩 실패] {file_path} → {e}")
            return ""
    except Exception as e:
        print(f"[파일 읽기 실패] {file_path} → {e}")
        return ""

def get_file_type(file_path):
    return os.path.splitext(file_path)[-1].lstrip(".")

def format_semgrep_results(results, extracted_path):
    issues = []

    for result in results["results"]:
        abs_path = result["path"]  # Semgrep에서 반환한 절대 경로
        rel_path = os.path.relpath(abs_path, extracted_path).replace("\\", "/")  # 상대 경로

        line_num = result["start"]["line"]

        issue = {
            "path": rel_path,
            "start": result["start"],
            "end": result["end"],
            "check_id": result["check_id"],
            "extra": result["extra"],
            "source_line": get_line_content(abs_path, line_num),
            "file_type": get_file_type(abs_path)
        }
        issues.append(issue)

    return issues
