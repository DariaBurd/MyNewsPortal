from django import template

register = template.Library()


@register.filter
def censor(value):
    forbidden_words = ['редиска', 'нехороший', 'плохой']  # Запрещённые слова
    if not isinstance(value, str):
        return value

    for word in forbidden_words:   # Заменяем все буквы, кроме первой, на *
        if word in value.lower():
            censored = word[0] + '*' * (len(word) - 1)
            value = value.replace(word, censored)
    return value