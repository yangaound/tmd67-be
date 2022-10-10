from typing import List

import strawberry

from tmd67_be.api.types import Path, Project


@strawberry.type
class Query:
    paths: List[Path] = strawberry.django.field()
    projects: List[Project] = strawberry.django.field()


schema = strawberry.Schema(query=Query)
