## Setup

1.  Clone this repository.
2.  Create a `.env` file in the root of the repository.
3.  Add the team's Gemini API key to the `.env` file:
    ```.env
    GEMINI_API_KEY=your_api_key_goes_here
    PIPENV_IGNORE_VIRTUALENVS=1
    ```
4.  Install the dependencies and activate the virtual environment:
    ```sh
    pipenv install
    pipenv shell
    ```
5.  Create two new folders in the repository's root: `context/` and `outputs/`.

## Usage

1.  Place the model's context files (e.g., ETL code, SQL definitions, or other documentation) into the `context/` folder.

2.  From the terminal (with the `pipenv shell` activated), run the main script:

    ```sh
    python main.py get_model_metadata <your_schema_name> <your_model_name>
    ```

      * **Important:** Replace `<your_schema_name>` and `<your_model_name>` with the actual schema and model that should be documented.

3.  The script will analyze the context and save three new CSV files in the `outputs/` folder (e.g., `<your_model_name>_AllColumnDescriptions.csv`, `<your_model_name>_AllColumnSpecs.csv`, `<your_model_name>_AllTableSpecs.csv`).

## Important: Merging with Our Data Dictionary

The script generates new descriptions for *all* columns every time it runs. It does **not** read the existing Data Dictionary, so it will create new descriptions for common columns (like `PPN_DTM` or `PA_SU_ID`) that we may already have documented.

### Recommended Workflow

1.  Run the script to generate the new CSVs in the `outputs/` folder.
2.  Manually copy the **new** information from the CSVs into our Data Dictionary.
3.  When you see a common column (`PPN_DTM`, etc.), **ignore the script's new description** and keep the one we already have. This prevents duplicate or conflicting descriptions.
