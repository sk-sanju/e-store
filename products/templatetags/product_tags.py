from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def get_rating_count(product, rating):
    return product.reviews.filter(rating=rating).count()

@register.filter
def get_rating_percent(product, rating):
    try:
        total = product.reviews.count()
        if total == 0:
            return 0

        count = product.reviews.filter(rating=rating).count()
        percent = (count / total) * 100

        return int(percent) 
    except:
        return 0
