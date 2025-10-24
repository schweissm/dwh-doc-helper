# Set-Up
1. Clone the repository and create a .env file inside the dwh-doc-helper folder.
2. Inside the .env file create a GEMINI_API_KEY variable and assign an API-Key.
3. Create a second PIPENV_IGNORE_VIRTUALENVS=1 variable inside the .env file.
4. Run `pipenv install` and then `pipenv shell`.
5. Create a **context** and **outputs** folder inside the root folder of the repo.

# Usage
Put plain text files with content like the ETL-Code or other documentation inside the **context** folder.
To generate the table and column descriptions use this command in the terminal `py main.py get_model_metadata schema_name model_name`.
