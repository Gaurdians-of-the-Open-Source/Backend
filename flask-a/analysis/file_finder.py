import os

def find_source_files(directory, extensions=None):
    if extensions is None:
        # Semgrep 지원 언어 확장자 전체 목록
        extensions = [
            ".py", ".java", ".js", ".jsx", ".ts", ".tsx", ".go", ".rb", ".php",
            ".c", ".cpp", ".cs", ".kt", ".kts", ".swift", ".scala",
            ".html", ".vue", ".json", ".yaml", ".yml", ".xml",
            ".jsp", ".jspf", ".pl", ".rs", ".rkt", ".dart"
        ]

    files_by_extension = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                full_path = os.path.join(root, file)
                ext_key = ext.lstrip(".")
                if ext_key not in files_by_extension:
                    files_by_extension[ext_key] = []
                files_by_extension[ext_key].append(full_path)

    return files_by_extension
