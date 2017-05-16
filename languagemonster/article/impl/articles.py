from django.core.paginator import Paginator

from core.models import Article

_ARTICLES_PER_PAGE = 20

def get_newest_articles(count=10):
    return Article.objects.order_by('-id')[:count]

def get_language_articles(lang_pair):
    return Paginator(
        Article.objects.filter(lang_pair=lang_pair).order_by('-id'),
        _ARTICLES_PER_PAGE,
    )

def get_article(article_id):
    return Article.objects.filter(id=article_id).first()
