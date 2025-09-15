import os
import great_expectations as gx
import pandas as pd
from dotenv import load_dotenv
import urllib.parse
from great_expectations.checkpoint import (
    Checkpoint,
    SlackNotificationAction,
    UpdateDataDocsAction
)

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
            
    def add_custom_expectation_to_suite(self,expectation_suite_name,expect_func_obj,col_effect):
        pass

    def create_batch_request(self,data_source_name,data_asset_name,batch_definition_name):
        file_data_asset = self._context.data_sources.get(data_source_name).get_asset(data_asset_name)
        
        try:
            file_data_asset.add_batch_definition(name=batch_definition_name)
            print(f"Created batch definition {batch_definition_name}")
        except Exception as e:
            print(f"{e}")
    
    def get_batch(self,data_source_name,data_asset_name,batch_definition_name):
        batch_definition = (
            self._context.data_sources.get(data_source_name)
            .get_asset(data_asset_name)
            .get_batch_definition(batch_definition_name)
        )
        return batch_definition
    
    def create_validator(self,data_source_name, data_asset_name, batch_name, suite_name, validator_name):
        expect_suite = self._context.suites.get(suite_name)
        batch_definition = (
            self._context.data_sources.get(data_source_name)
            .get_asset(data_asset_name)
            .get_batch_definition(batch_name)
        )
        try: 
            validation_definition = gx.ValidationDefinition(
                data=batch_definition,
                    suite=expect_suite,
                    name=validator_name
                )
            self._context.validation_definitions.add(validation_definition)
            print(f"Created validator {validator_name}")
        except Exception as e:
            print(f"{e}")

    def run_validator(self,validator_name):
        try:
            validation_definition = self._context.validation_definitions.get(validator_name)
            validation_results = validation_definition.run()
            print(validation_results)
        except Exception as e:
            print(f"{e}")

    def create_checkpoint_docs(self,checkpoint_name,list_validator_name):
        try:
            validation_definitions = [self._context.validation_definitions.get(validator_name) for validator_name in list_validator_name]
            action = UpdateDataDocsAction(name="update_data_docs")
            checkpoint = Checkpoint(
                name=checkpoint_name,
                validation_definitions=validation_definitions,  
                actions=action,
                result_format={"result_format": "SUMMARY"}
            )
            
            self._context.checkpoints.add(checkpoint)
        except Exception as e:
            print(f"{e}")
            
    def run_checkpoint(self,checkpoint_name):
        try:
            checkpoint = self._context.checkpoints.get(checkpoint_name)
            checkpoint.run()
        except Exception as e:
            print(f"{e}")
            
if __name__ == "__main__":
    gx_obj = GXClass(datasource_name="job_database")
    gx_obj.create_datasource()
    gx_obj.create_asset(asset_name="job_database",table_name="jobs")
    gx_obj.create_expectation_suite(expectation_suite_name="recent_suite")
    gx_obj.create_batch_request(data_source_name="job_database",data_asset_name="job_database",batch_definition_name="recent_batch")
