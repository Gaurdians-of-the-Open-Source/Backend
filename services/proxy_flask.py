import aiohttp
import tempfile

FLASK_SERVER_URL = "http://localhost:5000/analyze"  # Flask 서버 주소

async def send_to_flask_analyzer(zip_file, json_file):
    # 1. zip 파일을 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False) as tmp_zip:
        tmp_zip.write(await zip_file.read())
        tmp_zip_path = tmp_zip.name

    # 2. json 파일을 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False) as tmp_json:
        tmp_json.write(await json_file.read())
        tmp_json_path = tmp_json.name

    # 3. Flask 서버에 multipart/form-data 요청 보내기
    async with aiohttp.ClientSession() as session:
        with open(tmp_zip_path, "rb") as zf, open(tmp_json_path, "rb") as jf:
            form = aiohttp.FormData()
            form.add_field("zip", zf, filename="project.zip", content_type="application/zip")
            form.add_field("json", jf, filename="vulns.json", content_type="application/json")

            async with session.post(FLASK_SERVER_URL, data=form) as resp:
                if resp.status != 200:
                    raise Exception(f"Flask 서버 오류: {resp.status}")
                result = await resp.json()
                return result
