from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from boxes.models import Box


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home', 'subscribe_options', 'about'] 

    def location(self, item):
        return reverse(item)


class BoxSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Box.objects.filter(is_archived=True)

    def location(self, obj):
        return reverse('box_detail', args=[obj.slug])