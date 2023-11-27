from django import template

register = template.Library()


@register.filter(name="remove_spaces")
def remove_spaces(value):
    return str(value).replace(" ", "")


@register.filter(name="average_ratings")
def average_ratings(value):
    value = list(value)
    value = [int(i) for i in value]
    value = [i for i in value if i != 0]
    if sum(value) == 0:
        return 0
    return sum(value) / len(value)


@register.filter(name="title_case")
def title_case(value):
    return str(value).title()


@register.filter
def get_range(value):
    return range(1, value + 1)
