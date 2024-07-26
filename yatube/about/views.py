from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['st_tittle'] = 'А это страница обо мне'
        context['st_text'] = 'тут о том, какой я хороший'

        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['st_tittle'] = 'А это страница о том, что я уже узнал и использовал'
        context['st_text'] = 'Питончик, а еще Джанго, но последний трудно идет'

        return context
