# forwarder.py
import os
import time
import re
import urllib.parse
import requests
from typing import Optional, Tuple

# B 서버 기본 주소: 환경변수 FLASK_B_BASE_URL로 덮어쓸 수 있음
DEFAULT_FLASK_B_BASE = os.environ.get("FLASK_B_BASE_URL", "http://127.0.0.1:5001")

# Flask B의 수신 엔드포인트 (B의 app.py에서 /deep-analyze 사용 중)
RECEIVE_ENDPOINT = "/deep-analyze"

class ForwardError(Exception):
    pass

def _exists_or_raise(path: str, kind: str):
    if not os.path.exists(path):
        raise ForwardError(f"{kind} not found: {path}")

def _parse_filename_from_cd(content_disposition: str) -> Optional[str]:
    """
    Content-Disposition 헤더에서 파일명 파싱 (RFC 5987/6266 일부 대응)
    """
    if not content_disposition:
        return None

    # filename*=UTF-8''encoded-name.pdf
    m = re.search(r'filename\*\s*=\s*([^\'"]+)\'\'([^;]+)', content_disposition, flags=re.IGNORECASE)
    if m:
        enc, name = m.groups()
        try:
            return urllib.parse.unquote(name, encoding=enc, errors="replace")
        except Exception:
            return urllib.parse.unquote(name)

    # filename="name.pdf" 또는 filename=name.pdf
    m = re.search(r'filename\s*=\s*"?([^";]+)"?', content_disposition, flags=re.IGNORECASE)
    if m:
        return m.group(1)

    return None

def send_to_flask_b(
    job_id: str,
    source_zip_path: str,
    issues_json_path: str,
    flask_b_base_url: Optional[str] = None,
    timeout_sec: int = 600,
    retries: int = 1,
    accept: str = "application/pdf",
) -> Tuple[bytes, str, Optional[str]]:
    """
    Flask B의 /deep-analyze 로 멀티파트 업로드 → 응답 바디/콘텐츠타입/파일명 추출.
    반환: (body_bytes, content_type, filename_or_none)
    """
    base = (flask_b_base_url or DEFAULT_FLASK_B_BASE).rstrip("/")
    url = f"{base}{RECEIVE_ENDPOINT}"

    _exists_or_raise(source_zip_path, "source_zip")
    _exists_or_raise(issues_json_path, "issues_json")

    headers = {"Accept": accept}

    last_err = None
    for attempt in range(retries + 1):
        try:
            with open(source_zip_path, "rb") as f_zip, open(issues_json_path, "rb") as f_json:
                files = {
                    "source_zip": ("source.zip", f_zip, "application/zip"),
                    "json_file":  ("issues.json", f_json, "application/json"),
                }
                data = {"job_id": job_id}

                resp = requests.post(
                    url,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=timeout_sec,
                    stream=True,
                )
                resp.raise_for_status()

                content_type = resp.headers.get("Content-Type", "") or ""
                body = resp.content

                # 파일명 파싱 (PDF일 때 다운로드 이름으로 활용)
                cd = resp.headers.get("Content-Disposition", "") or ""
                filename = _parse_filename_from_cd(cd)

                return body, content_type, filename

        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.0)
                continue
            break

    raise ForwardError(f"Failed to obtain response from Flask B: {last_err}")
