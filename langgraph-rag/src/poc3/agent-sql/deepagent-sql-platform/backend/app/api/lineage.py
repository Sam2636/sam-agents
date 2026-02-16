from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def lineage_health():
    return {"status": "lineage ok"}
