from typing import List

import strawberry

from tmd67_be.api import types


@strawberry.type
class Query:
    paths: List[types.Path] = strawberry.django.field()
    projects: List[types.Project] = strawberry.django.field()
    levels: List[types.Level] = strawberry.django.field()


schema = strawberry.Schema(query=Query)
