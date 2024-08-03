from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source=".",
        entrypoint="getting_started.py:repo_info",
    ).deploy(
        name="my-first-deployment",
        work_pool_name="my-managed-pool",
        cron="*/1 * * * *",  # Closest cron equivalent to every 30 seconds (every minute)
    )
