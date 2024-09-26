from django.core.management.base import BaseCommand
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, Tokenizer, HashingTF, IDF
from pyspark.sql.functions import col, udf, row_number
from pyspark.sql.types import DoubleType
from pyspark.sql import Window
import numpy as np
import h5py


class Command(BaseCommand):
    help = 'create model book recommendations in .h5 file'

    def handle(self, *args, **kwargs):
        # Start a Spark session with 10GB of memory for both the driver and executor
        spark = SparkSession.builder \
            .appName("BookRecommendationSystem") \
            .master("local[*]") \
            .config("spark.driver.memory", "10g") \
            .config("spark.executor.memory", "10g") \
            .getOrCreate()

        # Read in the CSV file, filtering out any rows with missing values
        df = spark.read.csv("filtered_books.csv", header=True, inferSchema=True)
        df = df.filter(df.title.isNotNull() & df.average_rating.isNotNull())

        # Drop any columns that we don't need
        df = df.select("asin", "title", "author_name", "average_rating", "description")
        # Limit to a manageable number of rows for testing
        df = df.limit(1000)

        # Tokenize the title column
        title_tokenizer = Tokenizer(inputCol="title", outputCol="title_tokens")
        df = title_tokenizer.transform(df)

        # Hash the title tokens to a fixed length
        hashingTF_title = HashingTF(inputCol="title_tokens", outputCol="title_tf", numFeatures=10000)
        df = hashingTF_title.transform(df)

        # Apply TF-IDF to the title tokens
        idf_title = IDF(inputCol="title_tf", outputCol="title_tfidf")
        idf_model = idf_title.fit(df)
        df = idf_model.transform(df)

        # Assemble the title features into a single vector
        assembler = VectorAssembler(inputCols=["title_tfidf"], outputCol="features")
        df = assembler.transform(df)

        # Drop any rows with null features
        df_filtered = df.filter(df.features.isNotNull())

        # Define a function to calculate the cosine similarity between two vectors
        def cosine_similarity(v1, v2):
            if v1 is None or v2 is None:
                return float(0)
            
            v1_array = v1.toArray()
            v2_array = v2.toArray()
            
            norm_v1 = np.linalg.norm(v1_array)
            norm_v2 = np.linalg.norm(v2_array)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return float(0)
            
            return float(np.dot(v1_array, v2_array) / (norm_v1 * norm_v2))

        # Create a UDF for cosine similarity
        cosine_sim_udf = udf(cosine_similarity, DoubleType())

        # Join the filtered DataFrame with itself to get the similarity between books
        df_with_sim = df_filtered.alias("i").join(df_filtered.alias("j"), col("i.asin") != col("j.asin"))

        # Calculate the cosine similarity for each pair of books
        df_with_sim = df_with_sim.withColumn("similarity", cosine_sim_udf(col("i.features"), col("j.features")))

        # Generate top 5 recommendations for each book
        window_spec = Window.partitionBy("i.asin").orderBy(col("similarity").desc())
        top_recommendations = df_with_sim.withColumn("rank", row_number().over(window_spec)) \
                                        .filter(col("rank") <= 5) \
                                        .select(col("i.asin").alias("asin_i"), col("j.asin").alias("asin_j"), "similarity")

        # Show top recommendations
        top_recommendations.show(truncate=False)

        # Save model as H5 file
        def save_model_as_h5(df_sim):
            recommendations = df_sim.select("asin_i", "asin_j", "similarity").collect()

            asin_i = [row.asin_i for row in recommendations]  # Use new field names
            asin_j = [row.asin_j for row in recommendations]  # Use new field names
            similarities = [row.similarity for row in recommendations]  # Use dot notation

            with h5py.File("book_recommendation_model.h5", "w") as hf:
                hf.create_dataset("asin_i", data=np.array(asin_i, dtype="S"))
                hf.create_dataset("asin_j", data=np.array(asin_j, dtype="S"))
                hf.create_dataset("similarity", data=np.array(similarities, dtype=np.float64))

        save_model_as_h5(top_recommendations)

        # Stop the Spark session
        spark.stop()

        self.stdout.write(self.style.SUCCESS('Pre-data added successfully'))
