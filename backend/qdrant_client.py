from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PayloadSchemaType
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    "https://9485db48-8672-469a-a917-41a4ebbfd533.us-east4-0.gcp.cloud.qdrant.io"
)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "TalentScout"

qdrant_client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False,
    timeout=30,
    check_compatibility=False,
)

def create_collection():
    collections = [col.name for col in qdrant_client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )
    # Create payload indexes for filtering
    for field in ["session_id", "email"]:
        try:
            qdrant_client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception as e:
            if "already exists" in str(e).lower():
                pass
            else:
                print(f"Error creating index for {field}: {e}")

def store_candidate(candidate_dict):
    dummy_vector = [float(hash(candidate_dict.get("full_name", "")) % 1) for _ in range(128)]
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            {
                "id": hash(candidate_dict.get("email", "")) % (10 ** 8),
                "payload": candidate_dict,
                "vector": dummy_vector
            }
        ]
    )

def delete_session_data(session_id: str) -> bool:
    from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector

    session_filter_condition = Filter(
        must=[
            FieldCondition(
                key="session_id",
                match=MatchValue(value=session_id)
            )
        ]
    )

    try:
        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=FilterSelector(filter=session_filter_condition)
        )
        print(f"Deleted all points with session_id={session_id} from {COLLECTION_NAME}.")
        return True
    except Exception as e:
        print(f"Error deleting session data for session_id={session_id}: {e}")
        return False
