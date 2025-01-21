from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(queryset, page_number, per_page=10):
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        return paginator.page(1)
