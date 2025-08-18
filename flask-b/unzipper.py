import zipfile
def extract_zip(file_path, extracted_path):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        zip_file.extractall(extracted_path)
    print(f'압축 해제 완료: {file_path} → {extracted_path}')