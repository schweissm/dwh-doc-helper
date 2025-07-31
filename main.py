from core.get_context import *
import os
import shutil
from google import genai
from tqdm import tqdm

def create_context(project: str) -> None:

    with open(f'input/{project}/mart_columns.csv', 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    col_model_relations = []
    for line in lines:
        cols = line.split(',')
        row = {'column': cols[0], 'models': cols[1].split(';')}
        col_model_relations.append(row)

    # Wir generieren die Kontext-Daten für die Spalten-Tabellen Relationen
    context = []
    already_retrieved_models = []
    for relation in tqdm(col_model_relations[11:]):
        print(f'\nPROCESSING: {relation}\n')
        for model in relation['models']:
            # Create the direct lineage file
            get_direct_lineage(
                manifest_path=f'input/{project}/manifest.json',
                catalog_path=f'input/{project}/catalog.json',
                models=f'+{model}',
                dialect='bigquery'
            )

            # Create the recursive lineage for the column starting from the tables direct lineage
            get_recursive_lineage(
                model_name=model,
                column_name=relation['column']
            )

            # Load the content of the column lineage JSON file
            lineage_json_name = f'model_{project.replace('-', '_')}_{model}_{relation['column'].upper()}_ancestors.json'
            with open(os.path.join('outputs', lineage_json_name), encoding='utf-8') as f:
                column_lineage_data = json.load(f)

            # Get a list of all models inside the column-level lineage and the top-level model
            model_list = get_all_models_from_lineage(column_lineage_data)
            model_list.append(model)

            # Remove all models that were already retrieved (gathered code for context) and update the retrieved model list
            model_list = [model for model in model_list if not model in already_retrieved_models]
            already_retrieved_models += model_list

            # For all the remaining models in the list, get the code inside the compiled dbt-model files
            code = get_code_of_all_models(model_list)

            # Add the lineage data and the code to the context (check if a model is already inside the context)
            context += [
                f'### LINEAGE FOR {relation['column']} COLUMN FROM PARENT TABLE {model} DOWNWARDS ###\n\n{json.dumps(column_lineage_data, indent=2)}',
                code
            ]

            # Move the generated files into a new folder
            destination_folder = f'outputs/{project}/{relation['column']}/{model}'
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            for file_name in [f for f in os.listdir('outputs') if os.path.isfile(os.path.join('outputs', f))]:
                source_path = os.path.join('outputs', file_name)
                destination_path = os.path.join(destination_folder, file_name)
                shutil.move(source_path, destination_path)

        # Save the gathered context for the column
        with open(f'outputs/{project}/{relation['column']}/context.txt', 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(context))

def create_doc_blocks(project: str) -> None:

    # Init the GEMINI-client and load the prompt template
    client = genai.Client()
    with open('templates/gen_column_spec.txt', encoding='utf-8') as f:
        prompt_template = f.read()

    for column in os.listdir(os.path.join('outputs', project)):
        # Load the context of the column
        path_to_context = os.path.join('outputs', project, column, 'context.txt')
        with open(path_to_context, encoding='utf-8') as f:
            context = f.read()
        
        # Create the description
        response = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=prompt_template.format(column=column, context=context, language='English'),
        )

        # Create the doc-block
        doc_block = []
        doc_block.append('{% ' + f'{column}_DESC' + ' %}')
        doc_block.append(response.text)
        doc_block.append('{% enddocs %}\n\n')


        with open(f'docs/{project}_docs.md', 'a', encoding='utf-8') as f:
            f.write('\n'.join(doc_block))

if __name__ == '__main__':

    project = 'dwh-lkw'

    create_context(project)
    #create_doc_blocks(project)
