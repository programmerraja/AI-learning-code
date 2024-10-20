from trulens.apps.custom import instrument
from trulens.core import TruSession
from trulens.connectors.snowflake import SnowflakeConnector

connector = SnowflakeConnector(
    account="cortexsearchsummitdemo.preprod8.us-west-2.aws",
    user="admin",
    password="haq9NYF5gej*wvj8tbn",
    database="CORTEX_SEARCH_DB",
    role="ACCOUNTADMIN",
    warehouse="TRULENS_EXP",
    schema="EVAL_TEST",
)
session = TruSession(   
    connector=connector
)
session.reset_database()