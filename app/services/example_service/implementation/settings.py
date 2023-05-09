from pydantic import BaseSettings


class ExampleServiceParams(BaseSettings):
    EXAMPLE_PARAM: str

    class Config:
        env_prefix = "EXAMPLE_SERVICE_NAME_"
