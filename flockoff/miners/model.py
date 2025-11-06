import os
from huggingface_hub import HfApi
import bittensor as bt


def upload_data(repo_name: str, local_file_path: str) -> str:
    api = HfApi(token=os.environ["HF_TOKEN"])
    
    # Check if path is a directory or file
    if os.path.isdir(local_file_path):
        # If directory, look for data.jsonl inside it
        jsonl_file = os.path.join(local_file_path, "data.jsonl")
        if os.path.exists(jsonl_file):
            local_file_path = jsonl_file
            bt.logging.info(f"Found data.jsonl in directory, using: {local_file_path}")
        else:
            raise ValueError(f"No data.jsonl found in directory: {local_file_path}")
    elif not os.path.isfile(local_file_path):
        raise ValueError(f"Path is not a file or directory: {local_file_path}")
    
    try:
        api.create_repo(
            repo_name,
            exist_ok=False,
            repo_type="dataset",
        )
    except Exception as e:
        bt.logging.info(
            f"Repo {repo_name} already exists. Will commit the new version."
        )
    commit_message = api.upload_file(
        path_or_fileobj=local_file_path,
        path_in_repo="data.jsonl",
        repo_id=repo_name,
        repo_type="dataset",
    )
    # get commit hash
    commit_hash = commit_message.oid
    bt.logging.debug(f"Commit hash: {commit_hash}")
    bt.logging.debug(f"Repo name: {repo_name}")
    return commit_hash
