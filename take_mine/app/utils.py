from django.core.paginator import Paginator


def get_page_context(posts, request):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "paginator": paginator,
        "page_number": page_number,
        "page_obj": page_obj,
    }