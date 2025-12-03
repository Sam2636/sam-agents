# parser.py
import re
from pathlib import Path
try:
    from clang.cindex import Index, Config
    CLANG_AVAILABLE = True
except Exception:
    CLANG_AVAILABLE = False

# If libclang present but not configured, user may need to set Config.set_library_file/path
# e.g. Config.set_library_file("C:/Program Files/LLVM/bin/libclang.dll")

CPP_EXT = {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}

def _regex_extract_functions(code: str):
    # simple but conservative regex to extract function signatures
    pattern = re.compile(r'([a-zA-Z_][\w:<>\s\*&]+)\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*\{', re.S)
    functions = []
    for m in pattern.finditer(code):
        ret = m.group(1).strip()
        name = m.group(2).strip()
        params_raw = m.group(3).strip()
        params = []
        if params_raw:
            for p in [x.strip() for x in params_raw.split(",") if x.strip()]:
                parts = p.rsplit(" ", 1)
                if len(parts) == 2:
                    ptype, pname = parts[0].strip(), parts[1].strip()
                else:
                    ptype, pname = parts[0].strip(), "arg"
                params.append({"name": pname, "type": ptype})
        functions.append({"name": name, "returnType": ret, "params": params})
    return functions

def _libclang_extract(file_path: str):
    index = Index.create()
    tu = index.parse(file_path)
    functions = []
    globals_ = []
    def visit(node):
        kind = node.kind.name
        if kind == "FUNCTION_DECL":
            params = []
            # node.get_arguments()
            for a in node.get_arguments():
                params.append({"name": a.spelling, "type": a.type.spelling})
            functions.append({
                "name": node.spelling,
                "returnType": node.result_type.spelling if hasattr(node, "result_type") else node.type.spelling,
                "params": params
            })
        if kind == "VAR_DECL" and node.semantic_parent.kind.name == "TRANSLATION_UNIT":
            globals_.append({"name": node.spelling, "type": node.type.spelling})
        for c in node.get_children():
            visit(c)
    visit(tu.cursor)
    return functions, globals_

def parse_file_to_json(file_path: str):
    p = Path(file_path)
    ext = p.suffix.lower()
    code = p.read_text(errors="ignore")
    result = {"file": p.name, "functions": [], "globals": [], "notes": []}

    if CLANG_AVAILABLE and ext in CPP_EXT:
        try:
            funcs, globals_ = _libclang_extract(str(p))
            result["functions"] = funcs
            result["globals"] = globals_
            return result
        except Exception as e:
            # fallback to regex if libclang fails
            result["notes"].append(f"libclang failed: {e}; falling back to regex")
    # regex fallback
    funcs = _regex_extract_functions(code)
    result["functions"] = funcs
    return result
