from pydantic import BaseModel, model_validator


class NoIdCreateModel(BaseModel):
    """Base model for create schemas that forbid id field"""
    model_config = {
        "extra": "forbid"
    }

    @model_validator(mode="before")
    def forbid_id(cls, values):
        if isinstance(values, dict) and "id" in values:
            raise ValueError("id cannot be provided for create requests")
        return values


class NoIdUpdateModel(BaseModel):
    """Base model for update schemas that forbid id field"""
    model_config = {
        "extra": "forbid"
    }

    @model_validator(mode="before")
    def forbid_id(cls, values):
        if isinstance(values, dict) and "id" in values:
            raise ValueError("id cannot be updated; remove it from the payload")
        return values
