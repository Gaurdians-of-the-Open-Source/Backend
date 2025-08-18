import os
import zipfile
import shutil
import json

UPLOAD_DIR = "uploads"
SEED_FILE = os.path.join(UPLOAD_DIR, "job_id_seed.txt")

def get_next_job_id():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(SEED_FILE):
        with open(SEED_FILE, "w") as f:
            f.write("1")
    with open(SEED_FILE, "r") as f:
        current = int(f.read().strip())

    next_id = current + 1
    with open(SEED_FILE, "w") as f:
        f.write(str(next_id))

    return f"job_{str(current).zfill(4)}"

def flatten_directory(root_path):
    index = 0
    mapping = {}

    for root, dirs, files in os.walk(root_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            src = os.path.join(root, file)
            short_name = f"file_{index}{ext}"
            dst = os.path.join(root_path, short_name)
            try:
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    rel_src = os.path.relpath(src, root_path)
                    mapping[short_name] = rel_src.replace("\\", "/")
                    index += 1
            except Exception:
                pass

    map_path = os.path.join(root_path, "flatten_map.json")
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

def save_and_unzip(file_storage):
    job_id = get_next_job_id()
    job_path = os.path.join(UPLOAD_DIR, job_id)
    zip_path = os.path.join(job_path, "input.zip")

    os.makedirs(job_path, exist_ok=True)
    file_storage.save(zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(job_path)

    subitems = os.listdir(job_path)
    if len(subitems) == 1:
        subdir = os.path.join(job_path, subitems[0])
        if os.path.isdir(subdir):
            print("[자동 진입] →", subdir)
            job_path = subdir

    return job_path
