from google import genai
import os

def parse_yaml_string_to_file(yaml_string: str, output_filename: str) -> None:
    """
    Parses a YAML string (possibly wrapped in Markdown code block markers)
    and writes the YAML content to a file.

    Args:
        yaml_string (str): The input YAML string, possibly with ```yaml ... ``` markers.
        output_filename (str): The name of the output YAML file.
    """
    import re

    # Remove Markdown code block markers if present
    # This regex removes ```yaml ... ``` or ``` ... ```
    cleaned = re.sub(r"^```(?:yaml)?\s*([\s\S]*?)\s*```$", r"\1", yaml_string.strip(), flags=re.MULTILINE)

    # Write the cleaned YAML to the output file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(cleaned)

def get_model_spec(model_name: str) -> None:
    """ Creates a dbt-Model specification based on the contents of the context folder. 
        The specification is saved as a YAML-file that can be moved into the dwh-repository.
        The model_name parameter should be the name of the dbt-model for which the specification should be generated.
    """    
    
    # Load all data from the context folder
    context = []
    for file in os.listdir('context'):
       with open(os.path.join('context', file), encoding='utf-8') as f:
          context.append({
             'name': file.split('\\')[-1].split('.')[0],
             'content': f.read()
          })
    context = [f"--- {e['name'].upper()} ---\n{e['content']}" for e in context]

    # Prompt the LLM to generate a dbt-Model specification
    with open('templates/gen_model_spec.txt', encoding='utf-8') as f:
       prompt = f.read()


    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-pro', 
        contents=prompt.format(context='\n\n'.join(context))
    )

    # Save the specification as YAML
    parse_yaml_string_to_file(response.text, f'output/{model_name}.yml')