"""
Custom sitemaps for the HobbyHub project.

Defines:
- StaticViewSitemap: sitemap entries for static pages.
- BoxSitemap: sitemap entries for archived box detail pages.
"""


from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from boxes.models import Box


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages like home, subscribe options, and about."""
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        """Return list of named URLs for static pages."""
        return ['home', 'subscribe_options', 'about']

    def location(self, item):
        """Return the URL for the given named URL."""
        return reverse(item)


class BoxSitemap(Sitemap):
    """Sitemap for archived subscription boxes."""
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        """Return all archived boxes to include in the sitemap."""
        return Box.objects.filter(is_archived=True)

    def location(self, obj):
        """Return the URL for a specific box detail page."""
        return reverse('box_detail', args=[obj.slug])
