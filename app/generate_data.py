import time
import random
import uuid
from datetime import datetime, timedelta
import argparse
from zoneinfo import ZoneInfo
from utils.postgres import save_conversation, save_feedback
from utils.utils import initialize_env_variables, load_json_document
from exceptions.exceptions import WrongCliParams


PROJECT_DIR = "/mnt/workspace/__ing/llming/DTC/course/app"

initialize_env_variables(PROJECT_DIR)

# Set the timezone to CET (Europe/Berlin)
TZ = ZoneInfo("Africa/Cairo")

# List of sample questions and answers
MODELS = ["ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"]
RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]


def get_random_answer(documents):
    conversation_id = str(uuid.uuid4())
    idx = random.randrange(0,len(documents))
    question = documents[idx]['question']
    course = documents[idx]['course']

    ## Uniform relevance distribution.
    relevance = random.choice(RELEVANCE)
    answer = documents[idx]['question']

    if relevance != "RELEVANT":
        idx = random.randrange(0,len(documents))
        answer = documents[idx]['question']
        if relevance == "PARTLY_RELEVANT":
            idx = random.randrange(0,len(documents))
            answer = answer + "\n" + documents[idx]['question']

    model = random.choice(MODELS)

    openai_cost = 0
    if model.startswith("openai/"):
        openai_cost = random.uniform(0.001, 0.1)

    answer_data = {
        "answer": answer,
        "response_time": random.uniform(0.5, 5.0),
        "relevance": relevance,
        "relevance_explanation": f"This answer is {relevance.lower()} to the question.",
        "model_used": model,
        "prompt_tokens": random.randint(50, 200),
        "completion_tokens": random.randint(50, 300),
        "total_tokens": random.randint(100, 500),
        "eval_prompt_tokens": random.randint(50, 150),
        "eval_completion_tokens": random.randint(20, 100),
        "eval_total_tokens": random.randint(70, 250),
        "openai_cost": openai_cost,
    }
    
    return conversation_id, question, course, model, answer_data


def generate_synthetic_data(documents, start_time, end_time):
    current_time = start_time
    conversation_count = 0
    print(f"Starting historical data generation from {start_time} to {end_time}")

    while current_time < end_time:
        conversation_id, question, course, model, answer_data =\
              get_random_answer(documents)

        save_conversation(conversation_id, question, answer_data, course, current_time, is_setup=True)
        print(
            f"Saved conversation: ID={conversation_id}, Time={current_time}, Course={course}, Model={model}"
        )

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time, is_setup=True)
            print(
                f"Saved feedback for conversation {conversation_id}: {'Positive' if feedback > 0 else 'Negative'}"
            )

        current_time += timedelta(minutes=random.randint(1, 15))

        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} conversations so far...")

    print(
        f"Historical data generation complete. Total conversations: {conversation_count}"
    )


def generate_live_data(documents):
    conversation_count = 0
    print("Starting live data generation...")
    while True:
        current_time = datetime.now(TZ)
        conversation_id, question, course, model, answer_data =\
              get_random_answer(documents)

        save_conversation(conversation_id, question, answer_data, course, current_time, is_setup=True)
        print(
            f"Saved live conversation: ID={conversation_id}, Time={current_time}, Course={course}, Model={model}"
        )

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time, is_setup=True)
            print(
                f"Saved feedback for live conversation {conversation_id}: {'Positive' if feedback > 0 else 'Negative'}"
            )

        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} live conversations so far...")

        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reading control parameters.")
    parser.add_argument('--live_only', type=str, required=False, help='Value of live_only')
    args = parser.parse_args()

    live_only = args.live_only

    if live_only == 'false' or not live_only:
        live_only = False
    elif live_only == 'true':
        live_only = True
    else:
        raise WrongCliParams(
            "`live_only` parameter must be either true, false, or leave plank."
        )

    ## ====> Load Documents
    documents_path = f'{PROJECT_DIR}/data/documents.json'
    documents = load_json_document(documents_path)

    print(f"Script started at {datetime.now(TZ)}")
    if not live_only:
        end_time = datetime.now(TZ)
        start_time = end_time - timedelta(hours=6)
        print(f"Generating historical data from {start_time} to {end_time}")
        generate_synthetic_data(documents, start_time, end_time)
        print("Historical data generation complete.")

    print("Starting live data generation... Press Ctrl+C to stop.")
    try:
        generate_live_data(documents)
    except KeyboardInterrupt:
        print(f"Live data generation stopped at {datetime.now(TZ)}.")
    finally:
        print(f"Script ended at {datetime.now(TZ)}")