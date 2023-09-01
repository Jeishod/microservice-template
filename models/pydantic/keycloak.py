from pydantic import (
    BaseModel,
    Field,
)


class OIDCUser(BaseModel):
    """Represents a user object of Keycloak, parsed from access token,

    Notes: Check the Keycloak documentation at https://www.keycloak.org/docs-api/15.0/rest-api/index.html for
    details. This is a mere proxy object.
    """

    sub: str
    iat: int
    exp: int
    scope: str | None = None
    email_verified: bool
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: str
    preferred_username: str | None = None
    realm_access: dict | None = None
    resource_access: dict | None = None
    extra_fields: dict = Field(default_factory=dict)

    @property
    def realm_roles(self) -> list[str]:
        """Realm roles of the user

        Returns:
            list[str]: If the realm access dict contains roles
        """
        if not self.realm_access:
            raise ValueError("The 'realm_access' section of the provided access token is missing.")
        try:
            return self.realm_access["roles"]
        except KeyError as e:
            raise ValueError(
                "The 'realm_access' section of the provided access token did not contain any 'roles'."
            ) from e

    def client_roles(self, client: str) -> list[str]:
        """Get client roles of the user

        Returns:
            list[str]: If the resource access dict contains roles
        """
        if not self.resource_access:
            raise ValueError("The 'resource_access' section of the provided access token is missing")
        try:
            return self.resource_access[client]["roles"]
        except KeyError as e:
            raise ValueError(
                f"The 'resource_access' section of the provided access token did not contain '{client}' with 'roles'"
            ) from e

    def __str__(self) -> str:
        """String representation of an OIDCUser"""
        return self.preferred_username
