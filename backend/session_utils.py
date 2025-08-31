from .qdrant_client import delete_session_data

def delete_session(session_id: str) -> bool:
    print(f"Initiating deletion for session_id={session_id}")
    success = delete_session_data(session_id)
    if success:
        print(f"Session data for {session_id} deleted successfully.")
    else:
        print(f"Failed to delete session data for {session_id}.")
    return success
