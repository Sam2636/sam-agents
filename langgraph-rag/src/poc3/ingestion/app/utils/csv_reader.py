import pandas as pd
from io import StringIO

def read_csv(file):
    content = file.file.read().decode("utf-8")
    df = pd.read_csv(
        StringIO(content),
        skip_blank_lines=True,
        engine="python"
    )
    return df.fillna("")   # 👈 VERY IMPORTANT
