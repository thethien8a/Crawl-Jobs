import os
import great_expectations as gx
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime, timedelta
load_dotenv()

class GXClass:
    def __init__(self, datasource_name):
        self._connection_string = r"postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            os.getenv("POSTGRES_USER"),
            urllib.parse.quote(os.getenv("POSTGRES_PASSWORD")),
            os.getenv("POSTGRES_HOST", "localhost"),
            os.getenv("POSTGRES_PORT", "5432"),
            os.getenv("POSTGRES_DB")
        )

        self._context = gx.get_context()
        self.datasource_name = datasource_name
       
    def create_datasource(self):
        try:
            datasources = self._context.list_datasources()
            if not any(d['name'] == self.datasource_name for d in datasources):
                self._context.data_sources.add_postgres(
                    connection_string=self._connection_string,
                    name=self.datasource_name
                )
                print(f"Created datasource {self.datasource_name}")
            else:
                print(f"Datasource {self.datasource_name} already exists, using existing datasource")
        except Exception as e:
            print(f"Error: {e}")

    def create_asset(self,asset_name,table_name):
        try:
            datasrc = self._context.data_sources.get(self.datasource_name)
            datasrc.add_table_asset(
                name=asset_name,
                table_name=table_name,
            )
            print(f"Created asset {asset_name}")
        except Exception as e:
            print(f"{e}")

    def create_expectation_suite(self,expectation_suite_name):
        try:
            suite = gx.ExpectationSuite(name=expectation_suite_name)
            suite = self._context.suites.add(suite)
            print(f"Created expectation suite {expectation_suite_name}")
        except Exception as e:
            print(f"{e}")

    def add_built_in_expectation_to_suite(self,expectation_suite_name,expect_func_obj,col_effect):
        try:
            suite = self._context.suites.get(expectation_suite_name)
            suite.add_expectation(expect_func_obj(column=col_effect))
            print(f"Added expectation to suite {expectation_suite_name}")
        except Exception as e:
            print(f"{e}")
    
    def create_recent_batch_request(self, asset_name, table_name, update_col_name, days_back=7):
        """Create a BatchRequest for the latest data using QueryAsset with SQL filter on update_date."""
        try:
            datasource = self._context.data_sources.get(self.datasource_name)
            
            # Build SQL query to filter latest data
            query = f"""
            SELECT * FROM {table_name}
            WHERE {update_col_name} >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            ORDER BY {update_col_name} DESC
            """
            
            # Add QueryAsset if it doesn't exist
            try:
                query_asset = datasource.get_asset(asset_name)
                print(f"QueryAsset {asset_name} already exists.")
            except:
                query_asset = datasource.add_query_asset(
                    name=asset_name,
                    query=query
                )
                print(f"Created QueryAsset {asset_name} with query for latest {days_back} days.")
            
            # Build BatchRequest
            batch_request = datasource.build_batch_request(data_asset_name=asset_name)
            print(f"Created BatchRequest for recent data.")
            return batch_request
            
        except Exception as e:
            print(f"Error creating recent batch request: {e}")
            return None
    
    def validate_batch(self, batch_request, expectation_suite_name):
        """Validate the batch using the expectation suite."""
        try:
            # Get or create suite
            try:
                suite = self._context.get_expectation_suite(expectation_suite_name)
            except:
                self.create_expectation_suite(expectation_suite_name)
                suite = self._context.get_expectation_suite(expectation_suite_name)
            
            # Create validator and run validation
            validator = self._context.get_validator(
                batch_request=batch_request,
                expectation_suite=suite
            )
            results = validator.validate()
            print(f"Validation results for suite {expectation_suite_name}:")
            print(results)
            return results
        except Exception as e:
            print(f"Error validating batch: {e}")
            return None
        
    
if __name__ == "__main__":
    gx_obj = GXClass(datasource_name="job_database")
    gx_obj.create_datasource()
    gx_obj.create_asset(asset_name="job_database",table_name="jobs")
    gx_obj.create_expectation_suite(expectation_suite_name="recent_suite")
    # Ví dụ sử dụng
    batch_request = gx_obj.create_recent_batch_request("recent_jobs_batch", "jobs", update_col_name="update_date")
    if batch_request:
        gx_obj.validate_batch(batch_request, "recent_suite")  # Giả sử suite đã tạo

