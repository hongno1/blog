from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post

class LatestPostFeed(Feed):
    title = '我的博客'
    link = '/blog/'
    description = '博客的新的帖子'

    def items(self):
        return Post.published.all()[:3]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.body, 20)


