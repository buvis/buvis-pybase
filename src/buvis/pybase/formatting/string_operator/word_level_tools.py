"""Word-level string operations.
WordLevelTools provides singularization and pluralization using the inflection library.
Certain words (e.g. minutes) are excluded from transformation.

Example:
    >>> WordLevelTools.pluralize('cat')
    'cats'
    >>> WordLevelTools.singularize('dogs')
    'dog'
"""

from inflection import pluralize as infl_pluralize
from inflection import singularize as infl_singularize


class WordLevelTools:
    @staticmethod
    def singularize(text: str) -> str:
        exceptions = ["minutes"]

        return text if text in exceptions else infl_singularize(text)

    @staticmethod
    def pluralize(text: str) -> str:
        exceptions = ["minutes"]

        return text if text in exceptions else infl_pluralize(text)
