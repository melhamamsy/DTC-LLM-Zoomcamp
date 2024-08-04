from prefect import flow
from prefect.runner.storage import GitRepository

if __name__ == "__main__":
    flow.from_source(
        source=GitRepository(
            url="https://github.com/melhamamsy/DTC-LLM-Zoomcamp.git",
            branch="development/orchestration"
        ),
        entrypoint="orchestration/prefect/runtime_info.py:my_flow",
    ).deploy(
        name="my-docker-deployment",
        work_pool_name="my-docker-pool",
        # cron="*/1 * * * *",
    )