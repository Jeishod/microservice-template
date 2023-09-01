from enum import StrEnum


class AuthFlow(StrEnum):
    LOCAL = "local"
    KEYCLOAK = "keycloak"
