from django import template

register = template.Library()

@register.filter(name='get_answer_for_question')
def get_answer_for_question(user_result, question):
    return user_result.get_answer_for_question(question)
