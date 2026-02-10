from fastapi import APIRouter, HTTPException
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

# =========================
# Neo4j Driver
# =========================
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "12345678")
)

def get_session():
    return driver.session()


# =========================
# Models
# =========================

class ColumnSchema(BaseModel):
    name: str
    datatype: str
    is_pk: bool = False
    is_fk: bool = False


class TableSchema(BaseModel):
    layer: str
    schema: str
    name: str
    type: str
    version: int
    columns: List[ColumnSchema]


class VersionLineage(BaseModel):
    source_version: str
    target_version: str

class FKLineage(BaseModel):
    src: str
    tgt: str


# =========================
# CREATE / UPSERT TABLE VERSION
# =========================
@router.post("/table")
def upsert_table(table: TableSchema):

    table_id = f"{table.layer}.{table.schema}.{table.name}"
    version_id = f"{table_id}.v{table.version}"

    with get_session() as session:

        session.run("""
        // deactivate old version
        MATCH (t:Table {id:$tid})-[:HAS_VERSION]->(ov:TableVersion {active:true})
        SET ov.active = false
        """, {"tid": table_id})

        for col in table.columns:
            col_id = f"{version_id}.{col.name}"

            session.run("""
            MERGE (l:Layer {id:$layer})
            MERGE (t:Table {id:$tid})
            MERGE (v:TableVersion {
                id:$vid,
                version:$ver,
                type:$type,
                active:true
            })
            MERGE (c:ColumnVersion {id:$cid})

            SET c.name=$cname,
                c.datatype=$dtype,
                c.is_pk=$is_pk,
                c.is_fk=$is_fk,
                c.active=true

            MERGE (l)-[:HAS_TABLE]->(t)
            MERGE (t)-[:HAS_VERSION]->(v)
            MERGE (v)-[:HAS_COLUMN]->(c)
            """, {
                "layer": table.layer,
                "tid": table_id,
                "vid": version_id,
                "ver": table.version,
                "type": table.type,
                "cid": col_id,
                "cname": col.name,
                "dtype": col.datatype,
                "is_pk": col.is_pk,
                "is_fk": col.is_fk
            })

    return {"status": "OK", "version": version_id}


# =========================
# READ APIs
# =========================

@router.get("/tables")
def list_tables():
    with get_session() as session:
        result = session.run("""
        MATCH (l:Layer)-[:HAS_TABLE]->(t:Table)
        RETURN l.id AS layer, t.id AS table
        """)
        return [r.data() for r in result]


@router.get("/table/{table_id}")
def get_table(table_id: str):
    with get_session() as session:
        result = session.run("""
        MATCH (t:Table {id:$id})-[:HAS_VERSION]->(v:TableVersion)
        RETURN t.id AS table, v.id AS version, v.active AS active
        """, {"id": table_id})
        return [r.data() for r in result]


@router.get("/table/version/{version_id}")
def get_table_version(version_id: str):
    with get_session() as session:
        result = session.run("""
        MATCH (v:TableVersion {id:$vid})-[:HAS_COLUMN]->(c)
        RETURN v.id AS version, c.id AS column, c.datatype AS datatype
        """, {"vid": version_id})
        return [r.data() for r in result]


# =========================
# UPDATE APIs
# =========================

@router.put("/column/{column_version_id}")
def update_column(column_version_id: str, datatype: str):

    with get_session() as session:
        res = session.run("""
        MATCH (c:ColumnVersion {id:$id, active:true})
        SET c.datatype=$datatype
        RETURN c
        """, {"id": column_version_id, "datatype": datatype})

        if not res.single():
            raise HTTPException(404, "Column version not found")

    return {"status": "Column updated"}


# =========================
# DELETE / DEACTIVATE APIs
# =========================

@router.delete("/column/{column_version_id}")
def deactivate_column(column_version_id: str):
    with get_session() as session:
        session.run("""
        MATCH (c:ColumnVersion {id:$id})
        SET c.active=false
        """, {"id": column_version_id})
    return {"status": "Column deactivated"}


@router.delete("/table/version/{version_id}")
def deactivate_table_version(version_id: str):
    with get_session() as session:
        session.run("""
        MATCH (v:TableVersion {id:$id})
        SET v.active=false
        """, {"id": version_id})
    return {"status": "Table version deactivated"}


@router.delete("/table/{table_id}")
def delete_table(table_id: str):
    with get_session() as session:
        session.run("""
        MATCH (t:Table {id:$id})
        DETACH DELETE t
        """, {"id": table_id})
    return {"status": "Table deleted"}


# =========================
# LINEAGE APIs
# =========================

@router.post("/lineage/table")
def add_table_lineage(l: VersionLineage):
    with get_session() as session:
        session.run("""
        MATCH (s:TableVersion {id:$src})
        MATCH (t:TableVersion {id:$tgt})
        MERGE (s)-[:DERIVED_FROM]->(t)
        """, {"src": l.source_version, "tgt": l.target_version})
    return {"status": "Table lineage added"}


@router.post("/lineage/column")
def add_column_lineage(l: VersionLineage):
    with get_session() as session:
        session.run("""
        MATCH (s:ColumnVersion {id:$src})
        MATCH (t:ColumnVersion {id:$tgt})
        MERGE (s)-[:MAPS_TO]->(t)
        """, {"src": l.source_version, "tgt": l.target_version})
    return {"status": "Column lineage added"}


@router.delete("/lineage/table")
def delete_table_lineage(l: VersionLineage):
    with get_session() as session:
        session.run("""
        MATCH (s:TableVersion {id:$src})-[r:DERIVED_FROM]->(t:TableVersion {id:$tgt})
        DELETE r
        """, {"src": l.source_version, "tgt": l.target_version})
    return {"status": "Table lineage removed"}


@router.delete("/lineage/column")
def delete_column_lineage(l: VersionLineage):
    with get_session() as session:
        session.run("""
        MATCH (s:ColumnVersion {id:$src})-[r:MAPS_TO]->(t:ColumnVersion {id:$tgt})
        DELETE r
        """, {"src": l.source_version, "tgt": l.target_version})
    return {"status": "Column lineage removed"}


@router.post("/lineage/fk")
def add_fk(fk: FKLineage):
    with get_session() as session:
        session.run("""
        MATCH (s:ColumnVersion {id:$src})
        MATCH (t:ColumnVersion {id:$tgt})
        MERGE (s)-[:FK_TO]->(t)
        """, {
            "src": fk.src,
            "tgt": fk.tgt
        })

    return {"status": "FK linked"}


@router.get("/graph/metrics")
def graph_metrics():
    with get_session() as session:

        result = session.run("""
        MATCH (l:Layer)
        OPTIONAL MATCH (l)-[:HAS_TABLE]->(t:Table)
        OPTIONAL MATCH (t)-[:HAS_VERSION]->(v:TableVersion {active:true})
        OPTIONAL MATCH (v)-[:HAS_COLUMN]->(c:ColumnVersion {active:true})
        RETURN
            l.id AS layer,
            count(DISTINCT t) AS tables,
            count(DISTINCT v) AS versions,
            count(DISTINCT c) AS columns
        """)

        layers = [r.data() for r in result]

        summary = {
            "layers": len(layers),
            "tables": sum(l["tables"] for l in layers),
            "versions": sum(l["versions"] for l in layers),
            "columns": sum(l["columns"] for l in layers),
        }

    return {
        "layers": layers,
        "summary": summary
    }

@router.get("/graph/visual")
def graph_visual():
    nodes = {}
    edges = []
    with get_session() as session:
        result = session.run("""
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN
            elementId(n) AS sid,
            labels(n)[0] AS slabel,
            coalesce(n.name, n.id) AS sname,
            elementId(m) AS tid,
            labels(m)[0] AS tlabel,
            coalesce(m.name, m.id) AS tname,
            type(r) AS rel


        """)

        for r in result:
            # source node
            nodes[r["sid"]] = {
                "id": r["sid"],
                "label": r["sname"],
                "group": r["slabel"]
            }

            # target node
            if r["tid"] is not None:
                nodes[r["tid"]] = {
                    "id": r["tid"],
                    "label": r["tname"],
                    "group": r["tlabel"]
                }

                edges.append({
                    "from": r["sid"],
                    "to": r["tid"],
                    "label": r["rel"],
                    "arrows": "to"
                })

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }
