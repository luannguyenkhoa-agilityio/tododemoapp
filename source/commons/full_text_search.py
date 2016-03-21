from django.db import models, connections
from djorm_pgfulltext.models import SearchManager, SearchManagerMixIn


class SearchManagerMixInExt(SearchManagerMixIn):

    def _parse_fields(self, fields):

        parsed_fields = set()
        related_fields = set()

        if fields is not None and isinstance(fields, (list, tuple)):
            for i, field in enumerate(fields):
                if '__' in field:
                    related_fields.add((field, None))
                else:
                    parsed_fields.add(i)
        if len(parsed_fields) > 0:
            parsed_fields = super(SearchManagerMixInExt, self)._parse_fields(parsed_fields)

        parsed_fields.update(related_fields)
        return parsed_fields