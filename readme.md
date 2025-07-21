# Set-Up
1. Clone the repository and create a .env file inside the dwh-doc-helper folder.
2. Inside the env file create a GEMINI_API_KEY variable and assign an API-Key.
3. Run `pipenv install` and then `pipenv shell`.
4. Create a **context** and **output** inside the root folder of the repo.

# Usage
The dwh-doc-helper creates dbt-model specifications in the form of YAML-files. The goal is here to facilitate the documentation and testing of the models. The basis for the documentation and tests are the context around the model which we provide to a LLM (Gemini) for reasoning. The context is provided in the form of text files that are put into the context folder. Each piece of context should be put inside it's own text file with a descriptive heading, because the heading is also used in the prompt for the LLM.

For example:
- model_code.txt - Containes the dbt-model code
- model_comments.txt - Comments from the Design Studio
- model_schema.txt - Schema of the result table
- model_path.txt - Full path of the model inside the dwh-repository

After providing all the context run this command `py main.py get_model_spec 'dwh-model-name'` to generate a YAML-file. 

**Important note!** <br>
The generated specifications are meant as a basis for further refinment. Always double-check wheter the output of dwh-doc-helper is correct, because an incorrect documentation is more detrimental than having no documentation at all. The same is true for the tests.
