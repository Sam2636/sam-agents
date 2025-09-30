
import os 
os.environ["PYSPARK_PYTHON"] = r"C:\Users\sam\Documents\projects\rag-project\langgraph-rag\venv\Scripts\python.exe" 
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\sam\Documents\projects\rag-project\langgraph-rag\venv\Scripts\python.exe"
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
print("HADOOP_HOME:", os.environ.get("HADOOP_HOME"))


# print(os.path.exists(r"C:\Users\sam\Documents\projects\rag-projet\langgraph-rag\src\sample_10million.csv"))
# -----------------------------
# Initialize Spark
# -----------------------------
spark = (SparkSession.builder
         .appName("MultiAgentCSV")
         .master("local[*]")
         .getOrCreate())

# -----------------------------
# Load CSV
# -----------------------------
df = spark.read.csv("sample_10million.csv", header=True, inferSchema=True)
print("Original Data:")
df.show(5)

# -----------------------------
# Agent 1: Age Filter (>38)
# -----------------------------
df_age = df.filter(col("age") > 38)
df_age.write.csv("age_filtered.csv", header=True, mode="overwrite")
print("Age-filtered CSV generated.")

# -----------------------------
# Agent 2: City Filter (New York)
# -----------------------------
df_city = df.filter(col("city") == "New York")
df_city.write.csv("city_filtered.csv", header=True, mode="overwrite")
print("City-filtered CSV generated.")

# Stop Spark
spark.stop()
