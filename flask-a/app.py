from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import uuid
import json

from analysis.unzip import save_and_unzip
from analysis.detector import analyze_project

# B로 보내는 유틸
from forwarder import send_to_flask_b

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # === 0) job_id 생성 ===
        job_id = request.form.get("job_id") or str(uuid.uuid4())
        job_upload_dir = os.path.join(UPLOADS_DIR, job_id)
        job_output_dir = os.path.join(OUTPUTS_DIR, job_id)
        os.makedirs(job_upload_dir, exist_ok=True)
        os.makedirs(job_output_dir, exist_ok=True)

        # === 1) 업로드 ZIP을 먼저 저장 (B로 보낼 원본 보존) ===
        zip_save_path = os.path.join(job_upload_dir, "source.zip")
        file.save(zip_save_path)

        # save_and_unzip에서 동일 파일 객체를 쓰길 원할 수 있으니 스트림 위치 초기화
        try:
            file.stream.seek(0)
        except Exception:
            pass

        # === 2) 압축 해제 ===
        extracted_path = save_and_unzip(file)
        print("[압축 해제 위치]", extracted_path)
        print("[압축 해제 후 내용]", os.listdir(extracted_path))

        # === 3) 상위 디렉토리 1개만 있으면 내부로 자동 진입 ===
        subitems = os.listdir(extracted_path)
        if len(subitems) == 1:
            subdir = os.path.join(extracted_path, subitems[0])
            if os.path.isdir(subdir):
                print("[자동 진입] →", subdir)
                extracted_path = subdir

        # === 4) 정적 분석 수행 ===
        formatted = analyze_project(extracted_path)

        # === 5) issues.json 저장 (outputs/{job_id}/issues.json) ===
        issues_path = os.path.join(job_output_dir, "issues.json")
        with open(issues_path, "w", encoding="utf-8") as f:
            json.dump(formatted, f, ensure_ascii=False, indent=2)

        # === 6) 즉시 Flask B로 전송 → B의 응답 그대로 리턴 ===
        # 기본은 PDF 바이너리, 만약 B가 JSON으로 응답하도록 구성되면 JSON도 그대로 전달됨.
        body, content_type, filename = send_to_flask_b(
            job_id=job_id,
            source_zip_path=zip_save_path,     # A가 받은 업로드 ZIP
            issues_json_path=issues_path,      # A가 만든 issues.json
            # flask_b_base_url 미지정 시 환경변수 FLASK_B_BASE_URL 또는 http://127.0.0.1:5001
            accept=request.headers.get("Accept", "application/pdf"),
        )

        # 콘텐츠 타입 보고 그대로 내려보냄
        resp = Response(body, mimetype=content_type if content_type else None)
        if filename:
            resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "Flask A"})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)

