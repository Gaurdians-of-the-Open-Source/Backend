from pathlib import Path

def make_dirs(base_dir):
    received = Path(base_dir) / 'received'
    extracted = Path(base_dir) / 'workspace' / 'extracted'
    files_dir = Path(base_dir) / 'workspace' / 'files'
    markdowns_dir = Path(base_dir) / 'workspace' / 'markdowns'
    output_dir = Path(base_dir) / 'workspace' / 'output'
    for p in (received, extracted, files_dir, markdowns_dir, output_dir):
        p.mkdir(parents=True, exist_ok=True)
    return {'received': received, 'extracted': extracted, 'files': files_dir, 
            'markdowns': markdowns_dir, 'output': output_dir}
