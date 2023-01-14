from typing import List

import strawberry_django
from strawberry import auto

from tmd67_be.api import models


@strawberry_django.filters.filter(models.Path, lookups=True)
class PathFilter:
    id: auto
    en_name: auto
    tw_name: auto
    show_name: auto
    initialism: auto


@strawberry_django.type(models.Path, filters=PathFilter, pagination=True)
class Path:
    id: auto
    en_name: auto
    tw_name: auto
    show_name: auto
    initialism: auto
    en_description: auto
    tw_description: auto
    levels: List["Level"]


@strawberry_django.filters.filter(models.Project, lookups=True)
class ProjectFilter:
    id: auto
    en_name: auto
    tw_name: auto
    show_name: auto


@strawberry_django.type(models.Project, filters=ProjectFilter, pagination=True)
class Project:
    id: auto
    en_name: auto
    tw_name: auto
    show_name: auto
    en_description: auto
    tw_description: auto
    en_purpose: auto
    tw_purpose: auto
    en_overview: auto
    tw_overview: auto
    en_includes: auto
    tw_includes: auto
    en_form: auto
    tw_form: auto
    levels: List["Level"]
    includes: List["ProjectInclude"]


@strawberry_django.filters.filter(models.ProjectInclude, lookups=True)
class ProjectIncludeFilter:
    id: auto
    en_name: auto
    tw_name: auto


@strawberry_django.type(
    models.ProjectInclude, filters=ProjectIncludeFilter, pagination=True
)
class ProjectInclude:
    id: auto
    en_name: auto
    tw_name: auto
    en_form: auto
    tw_form: auto
    project: Project


@strawberry_django.filters.filter(models.Level, lookups=True)
class LevelFilter:
    id: auto
    path: PathFilter
    project: ProjectFilter
    level: auto
    en_name: auto
    tw_name: auto
    is_elective: auto
    is_old: auto


@strawberry_django.type(models.Level, filters=LevelFilter, pagination=True)
class Level:
    id: auto
    path: Path
    project: Project
    level: auto
    en_name: auto
    tw_name: auto
    is_elective: auto
    elective_number: auto
    is_old: auto
