from typing import List

import strawberry
from strawberry import auto

from tmd67_be.api import models


@strawberry.django.type(models.Path)
class Path:
    id: auto
    en_name: auto
    tw_name: auto
    initialism: auto
    en_description: auto
    tw_description: auto
    projects: List["Project"]


@strawberry.django.type(models.Project)
class Project:
    id: auto
    path: "Path"
    level: auto
    is_elective: auto
    en_name: auto
    tw_name: auto
    en_description: auto
    tw_description: auto
    en_purpose: auto
    tw_purpose: auto
    en_overview: auto
    tw_overview: auto
    includes: auto
    evaluation_form: auto
