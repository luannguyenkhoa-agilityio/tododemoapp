from tastypie.paginator import Paginator


class NoLimitPaginator(Paginator):
    """
    Remove paginator
    """

    def get_slice(self, limit, offset):
        # Always get the first page
        return super(NoLimitPaginator, self).get_slice(0, 0)


class PageNumberPaginator(Paginator):
    def page(self):
        output = super(PageNumberPaginator, self).page()
        output['page_number'] = int(self.offset / self.limit) + 1
        return output
