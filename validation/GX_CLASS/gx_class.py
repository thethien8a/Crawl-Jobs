import os
import great_expectations as gx
from dotenv import load_dotenv
import urllib.parse
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
        
    def add_expectation_to_suite(self,expectation_suite_name,expect_func_obj,col_effect):
        try:
            suite = self._context.suites.get(expectation_suite_name)
            suite.add_expectation(expect_func_obj(column=col_effect))
            print(f"Added expectation to suite {expectation_suite_name}")
        except Exception as e:
            print(f"{e}")
    
    
        
if __name__ == "__main__":
    gx_obj = GXClass(datasource_name="job_database")
    gx_obj.create_datasource()
    gx_obj.create_asset(asset_name="job_database",table_name="jobs")
