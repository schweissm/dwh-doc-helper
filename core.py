from google import genai
import os
import hashlib
import pandas as pd
from io import StringIO

def send_llm_request(prompt_template_name: str, prompt_params: dict) -> str:
    
    # Prompt the LLM to generate column descriptions
    with open(f'templates/{prompt_template_name}.txt', encoding='utf-8') as f:
       prompt = f.read()

    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-pro', 
        contents=prompt.format(language=prompt_params['language'], context=prompt_params['context'])
    )

    return response.text

def get_model_metadata(schema_name: str, model_name: str) -> None:

    # Load all context for the LLM
    context = []
    for file in os.listdir('context'):
       with open(os.path.join('context', file), encoding='utf-8') as f:
          context.append({
             'name': file.split('\\')[-1].split('.')[0],
             'content': f.read()
          })
    context = [f"--- {e['name'].upper()} ---\n{e['content']}" for e in context]
    context = '\n\n'.join(context)

    
    # Prompt the LLM to generate column descriptions
    col_specs_csv_string = send_llm_request(prompt_template_name='gen_column_specs', prompt_params={'context': context, 'language': 'German'})
    df = pd.read_csv(StringIO(col_specs_csv_string), encoding='utf-8')

    # Generate a hashkey for the description 
    df['description_id'] = df['description'].apply(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())

    # Generate the CSV-data for the AllColumnSpecs und AllColumnDescriptions sheets
    df['schema_name'] = schema_name
    df['model_name'] = model_name
    df['data_type'] = ''

    df[['schema_name', 'model_name', 'column_name', 'data_type', 'description_id']].to_csv(f'outputs/{model_name}_AllColumnSpecs.csv', encoding='utf-8', index=False)
    df[['description_id', 'description']].to_csv(f'outputs/{model_name}_AllColumnDescriptions.csv', encoding='utf-8', index=False)

    # Prompt the LLM to generate a model description based on the column descriptions
    context = f'# Table Name: {model_name}\n\n' + df[['column_name', 'description']].to_csv(index=False)
    model_spec_csv_string = send_llm_request(prompt_template_name='gen_model_spec', prompt_params={'context': context, 'language': 'German'})
    
    with open(f'outputs/{model_name}_AllTableSpecs.csv', 'w', encoding='utf-8') as f:
       f.write('schema_name,model_name,description\n')
       f.write(f'{schema_name},{model_name},"{model_spec_csv_string}"')