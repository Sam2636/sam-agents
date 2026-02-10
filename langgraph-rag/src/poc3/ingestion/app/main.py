from fastapi import FastAPI
from app.ingest.schema import router as schema
from app.ingest.layer import router as layer
from app.ingest.transformations import router as transformations
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Metadata Ingestion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(schema, prefix="/metadata", tags=["Schema"])
app.include_router(layer, prefix="/metadata", tags=["Layer"])
app.include_router(transformations, prefix="/metadata", tags=["Transformations"])