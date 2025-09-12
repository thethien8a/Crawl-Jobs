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

        self.context = gx.get_context(mode="file")
        self.datasource_name = datasource_name
       
    def create_datasource(self):
        try:
            datasources = self.context.list_datasources()
            if not any(d['name'] == self.datasource_name for d in datasources):
                self.context.data_sources.add_postgres(
                    connection_string=self._connection_string,
                    name=self.datasource_name
                )
                print(f"Created datasource {self.datasource_name}")
            else:
                print(f"Datasource {self.datasource_name} already exists, using existing datasource")
        except Exception as e:
            print(f"Error: {e}")

    # def create_asset(self,table_name):
    #     try:
            
    #         datasrc = self.context.data_sources.get(self.datasource_name)
    #         datasrc.add_table_asset(
    #             table_name=table_name,
    #         )
    #     except Exception as e:
    #         print(f"{e}")

    # def 
    
if __name__ == "__main__":
    gx_obj = GXClass(datasource_name="job_database")
    gx_obj.create_datasource()
