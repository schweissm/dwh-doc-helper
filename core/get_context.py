import subprocess
import json
from pathlib import Path

def get_all_files(root_dir: str) -> list:
    root_path = Path(root_dir)
    file_paths = [str(path) for path in root_path.rglob('*.sql')]
    return file_paths

def get_code_of_all_models(models: list[str]) -> str:
    file_paths = get_all_files('input')
    
    code_list = []
    for model in models:
        for path in file_paths:
            if model == path.split('\\')[-1].replace('.sql', ''):
                with open(path, encoding='utf-8') as f:
                    code_list.append(
                        f'### SQL CODE FOR model.dwh_lkw.{model} ###\n\n{f.read()}'
                        )

    return '\n\n'.join(code_list)

def get_recursive_lineage(model_name, column_name):
    command = [
        'dbt_column_lineage_recursive',
        '--model', model_name,
        '--column', column_name
    ]
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )
    
    return result.stdout

def get_direct_lineage(manifest_path, catalog_path, models, dialect):
    command = [
        'dbt_column_lineage_direct',
        '--manifest', manifest_path,
        '--catalog', catalog_path,
        '--model', models,
        '--dialect', dialect
    ]

    # No output run
    # result = subprocess.run(
    #     command,
    #     capture_output=True,
    #     text=True,
    #     check=True
    # )
    
    # return result.stdout
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    output_lines = []
    
    # Read and print output in real-time
    for line in process.stdout:
        print(line, end='')  # Print to terminal immediately
        output_lines.append(line)
    
    # Wait for process to complete
    process.wait()
    
    # Check if process completed successfully
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
    
    # Return the complete output as a string
    return ''.join(output_lines)

def get_all_models_from_lineage(lineage_data: dict) -> list:
    
    model_names = []
    def find_names_recursive(d):
        if not isinstance(d, dict):
            return

        for key, value in d.items():
            # Heuristic to identify model names
            if 'model.' in key: #or 'source.' in key:
                model_names.append(key.split('.')[-1])
            
            # Recurse into the nested dictionary
            find_names_recursive(value)

    find_names_recursive(lineage_data)
    
    # Return a list of unique model names
    return list(set(model_names))