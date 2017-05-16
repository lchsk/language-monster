from django.http import Http404

from utility.views import ContextView
from utility.interface import get_lang_pair_from_slugs

from article.impl.articles import get_article, get_language_articles

from core.data.language_pair import LANGUAGE_PAIRS_FLAT

class ArticleView(ContextView):
    template_name = 'landing/article.html'

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)

        article = get_article(kwargs['article_id'])

        context['article'] = article
        context['language'] = LANGUAGE_PAIRS_FLAT[article.lang_pair]

        return context

class ArticlesView(ContextView):
    template_name = 'landing/articles.html'

    def get_context_data(self, **kwargs):
        context = super(ArticlesView, self).get_context_data(**kwargs)

        lang_pair = get_lang_pair_from_slugs(
            self._context.language.language.slug,
            kwargs['target_lang'],
        )

        page = int(kwargs.get('page', 1) or 1)
        articles = get_language_articles(lang_pair.symbol)
        num_pages = articles.num_pages

        if page < 1 or page > num_pages:
            raise Http404("Page not found")

        context['lang_slug'] = kwargs['target_lang']
        context['articles'] = articles.page(page)
        context['num_pages'] = num_pages
        context['current_page'] = page
        context['target_lang'] = lang_pair.target_language

        return context
