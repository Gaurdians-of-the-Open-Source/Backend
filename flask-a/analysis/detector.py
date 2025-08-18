import os
import subprocess
import json
from .file_finder import find_source_files
from .formatter import format_semgrep_results

SEMGREP_TIMEOUT = 60  # 전체 분석 여유 시간
MAX_CMD_LENGTH = 8000  # Windows 경로 길이 제한

def split_file_list(file_paths, max_length):
    """
    경로 총합이 max_length보다 넘지 않도록 분할
    """
    batches, current_batch, current_len = [], [], 0
    for path in file_paths:
        added_len = len(path) + 1  # 공백 포함
        if current_len + added_len > max_length:
            batches.append(current_batch)
            current_batch = [path]
            current_len = added_len
        else:
            current_batch.append(path)
            current_len += added_len
    if current_batch:
        batches.append(current_batch)
    return batches

def analyze_project(project_path):
    # 🔍 모든 코드 파일 수집
    files_by_ext = find_source_files(project_path)
    all_files = []
    for ext_files in files_by_ext.values():
        all_files.extend(ext_files)

    if not all_files:
        print("[!] 분석할 소스 파일이 없습니다.")
        return []

    results = []

    # 📦 Batch로 나눠서 Semgrep 실행
    batches = split_file_list(all_files, MAX_CMD_LENGTH)

    for i, batch in enumerate(batches):
        print(f"[Semgrep 실행] Batch {i+1}/{len(batches)}: {len(batch)} files")
        try:
            completed = subprocess.run(
                ["semgrep", "--config", "auto", *batch, "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",  # ✅ CP949 에러 방지
                timeout=SEMGREP_TIMEOUT
            )
            if completed.returncode == 0:
                json_output = json.loads(completed.stdout)
                results.extend(format_semgrep_results(json_output, project_path))
            else:
                print(f"[실패] batch {i+1}: {completed.stderr.strip()}")
        except Exception as e:
            print(f"[에러] batch {i+1}: {e}")

    print(f"[분석 완료] 총 발견된 취약점: {len(results)}개")
    return results
