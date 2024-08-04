sqlite3 ~/.prefect/prefect.db > .tables
prefect deployment run 'repo-info/my-first-deployment' -p repo_owner="melhamamsy" -p repo_name="DTC-LLM-Zoomcamp"

<!-- To reset your database, run the CLI command: -->
prefect server database reset -y