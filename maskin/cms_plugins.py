from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from aldryn_newsblog.cms_plugins import NewsBlogPlugin
from models import NewsBlogLatestArticleByCategory
from forms import NewsBlogLatestArticleByCategoryPluginForm


@plugin_pool.register_plugin
class NewsBlogLatestArticleByCategoryPlugin(NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/latest_articles.html'
    name = _('Latest Articles By Category')
    model = NewsBlogLatestArticleByCategory
    form = NewsBlogLatestArticleByCategoryPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['article_list'] = instance.get_articles(request)
        return context
