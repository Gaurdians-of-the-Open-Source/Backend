from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
from unzipper import extract_zip
from analyzer import (
    load_and_group_issues,
    save_grouped_issues,
    save_piece_markdowns,
    merge_markdowns_to_pdf,
)
# 'utils'는 더 이상 사용하지 않으므로 주석 처리하거나 삭제해도 됩니다.
# from utils import make_dirs 
import zipfile, json, uuid, shutil, traceback
import os # os 라이브러리를 import 합니다.

app = Flask(__name__)
CORS(app)

# --- 수정된 부분 시작 ---

# 공유 볼륨의 올바른 기본 경로를 .env 파일의 환경 변수에서 직접 가져옵니다.
# 이렇게 하면 컨테이너 내부 경로(/app)가 아닌 공유 볼륨 경로(/workspace)를 사용하게 됩니다.
SHARED_JOBS_DIR = Path(os.environ.get("WORKSPACE_DIR", "/workspace")) / 'jobs'

def _job_dirs(job_id: str) -> dict:
    """요청별 job_id 하위 디렉토리 생성(있으면 초기화)"""
    job_base = SHARED_JOBS_DIR / job_id
    
    # DIRS 변수를 사용하는 대신 올바른 절대 경로를 직접 생성합니다.
    paths = {
        "received":   job_base / "received",
        "extracted":  job_base / "extracted",
        "files":      job_base / "files",
        "markdowns":  job_base / "markdowns",
        "output":     job_base / "output",
    }

    # received/extracted/files/markdowns는 싹 비우고 다시 생성
    for k in ["received", "extracted", "files", "markdowns"]:
        p = paths[k]
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
        p.mkdir(parents=True, exist_ok=True)

    # output은 결과물 위치: 폴더만 보장 (덮어쓰기 허용)
    paths["output"].mkdir(parents=True, exist_ok=True)
    return paths

# --- 수정된 부분 끝 ---


@app.route('/deep-analyze', methods=['POST'])
def deep_analyze():
    if 'json_file' not in request.files or 'source_zip' not in request.files:
        return jsonify({'error': 'Missing files'}), 400

    json_file  = request.files['json_file']
    source_zip = request.files['source_zip']
    if not json_file.filename or not source_zip.filename:
        return jsonify({'error': 'Empty files'}), 400

    job_id = (request.form.get("job_id") or "").strip() or uuid.uuid4().hex
    J = _job_dirs(job_id)

    json_path = J['received'] / 'issues.json'
    zip_path  = J['received'] / 'source.zip'

    json_file.save(str(json_path))
    source_zip.save(str(zip_path))

    try:
        extract_zip(zip_path, J['extracted'])
        grouped = load_and_group_issues(json_path)
        save_grouped_issues(J['files'], grouped, J['extracted'])
        meta = save_piece_markdowns(J['files'], J['markdowns'])
        
        # analyzer.py의 merge_markdowns_to_pdf 함수가 pdf 경로를 반환하지 않을 수 있으므로,
        # 명시적으로 경로를 생성하고 해당 경로로 파일을 저장하도록 유도합니다.
        # 이 부분은 analyzer.py의 구현에 따라 달라질 수 있습니다.
        # 여기서는 pdf_path를 명시적으로 생성합니다.
        output_pdf_path = J['output'] / f"{meta.get('job_id', job_id)}.pdf"
        merge_markdowns_to_pdf(J['markdowns'], J['output'], meta)

        if not output_pdf_path.exists():
            return jsonify({'error': 'PDF not generated'}), 500

        accept = (request.headers.get('Accept') or '').lower()
        if 'application/pdf' in accept:
            return send_file(
                str(output_pdf_path),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{job_id}.pdf"
            )

        return jsonify({
            'message': 'ok',
            'job_id': job_id,
            'total': len(grouped),
            'processed_total': meta.get('processed_total'),
            'success_count': meta.get('success_count'),
            'skipped_count': meta.get('skipped_count'),
            'pdf_path': str(output_pdf_path),
        }), 200

    except (zipfile.BadZipFile, json.JSONDecodeError):
        return jsonify({'error': 'Bad request: invalid zip or json'}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal error', 'detail': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)