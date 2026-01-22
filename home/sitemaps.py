"""
Sitemap configuration for Jagoron News
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import News, NavbarItem, SubSection, Category, SiteInfo, Tag
from django.utils import timezone
from datetime import timedelta
from urllib.parse import quote


class NewsSitemap(Sitemap):
    """Regular sitemap for news articles"""
    changefreq = 'daily'
    priority = 0.8
    
    def items(self):
        """Return all published news articles"""
        return News.published.all().order_by('-created_at')
    
    def lastmod(self, obj):
        """Return the last modification date"""
        return obj.updated_at
    
    def location(self, obj):
        """Return the URL for the news article"""
        return obj.get_absolute_url()


class GoogleNewsSitemap(Sitemap):
    """
    Google News sitemap - only includes news from last 48 hours
    Must use custom template with Google News namespace
    """
    changefreq = 'always'
    priority = 1.0
    limit = 1000  # Google News max limit
    
    def items(self):
        """Return only news articles from the last 48 hours"""
        # Get news from last 48 hours
        # Use timezone-aware datetime
        now = timezone.now()
        cutoff_time = now - timedelta(hours=48)
        
        # Query for published news from last 48 hours
        # Use created_at (publication date) not updated_at
        # For scheduled news, use scheduled_publish_at if it exists and is in the past
        queryset = News.published.filter(
            created_at__gte=cutoff_time
        ).order_by('-created_at')[:1000]  # Max 1000 URLs
        
        # Debug: Log the query results
        import logging
        logger = logging.getLogger(__name__)
        count = queryset.count()
        logger.info(f"GoogleNewsSitemap.items(): Found {count} news items from last 48 hours (cutoff: {cutoff_time})")
        
        return queryset
    
    def lastmod(self, obj):
        """Return the publication date (created_at for Google News)"""
        return obj.created_at
    
    def location(self, obj):
        """Return the URL for the news article"""
        return obj.get_absolute_url()
    
    def get_publication_name(self):
        """Get the publication name from SiteInfo"""
        site_info = SiteInfo.objects.first()
        return site_info.name if site_info and site_info.name else "জাগরণ নিউজ"
    
    def get_publication_language(self):
        """Get the publication language"""
        return "bn"  # Bengali
    
    def get_news_title(self, obj):
        """Get the news title"""
        return obj.title or ''
    
    def get_news_publication_date(self, obj):
        """Get the publication date in ISO format with timezone"""
        # Use created_at for publication date
        pub_date = obj.created_at
        if pub_date:
            # Format: 2026-01-04T20:42:41+06:00
            return pub_date.strftime('%Y-%m-%dT%H:%M:%S+06:00')
        return None
    
    def get_news_keywords(self, obj):
        """Get keywords from categories"""
        keywords = []
        # Add category names as keywords
        for category in obj.category.all():
            if category.name:
                keywords.append(category.name)
        # Add section title if available
        if obj.section and obj.section.title:
            keywords.append(obj.section.title)
        # Add subsection title if available
        if obj.sub_section and obj.sub_section.title:
            keywords.append(obj.sub_section.title)
        return ', '.join(keywords) if keywords else ''
    
    def get_image_url(self, obj, request=None):
        """Get the image URL for the news article"""
        if obj.heading_image:
            if request:
                return request.build_absolute_uri(obj.heading_image.url)
            return obj.heading_image.url
        elif obj.main_image:
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None
    
    def get_image_caption(self, obj):
        """Get the image caption"""
        if obj.heading_image_title:
            return obj.heading_image_title
        elif obj.main_image_title:
            return obj.main_image_title
        elif obj.title:
            return obj.title
        return 'ছবি : সংগৃহীত'


class SectionSitemap(Sitemap):
    """Sitemap for sections and subsections"""
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        """Return all active sections and subsections"""
        items = []
        # Add sections
        for section in NavbarItem.objects.filter(is_active=True).order_by('position'):
            if section.english_title:  # Only include sections with slugs
                items.append({
                    'type': 'section',
                    'obj': section
                })
        
        # Add subsections
        for subsection in SubSection.objects.filter(is_active=True).select_related('section').order_by('position'):
            if subsection.english_title and subsection.section and subsection.section.english_title:
                items.append({
                    'type': 'subsection',
                    'obj': subsection
                })
        
        return items
    
    def lastmod(self, item):
        """Return the last modification date"""
        # Get the most recent news update for this section/subsection
        obj = item['obj']
        if item['type'] == 'section':
            latest_news = News.published.filter(section=obj).order_by('-updated_at').first()
        else:  # subsection
            latest_news = News.published.filter(sub_section=obj).order_by('-updated_at').first()
        
        if latest_news:
            return latest_news.updated_at
        return timezone.now()
    
    def location(self, item):
        """Return the URL for the section or subsection"""
        obj = item['obj']
        return obj.get_absolute_url()


class TopicSitemap(Sitemap):
    """Sitemap for topics (tags)"""
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        """Return all tags that have published news"""
        # Only include tags that have published news
        tags_with_news = Tag.objects.filter(
            news__isnull=False
        ).distinct()
        
        # Filter to only those with published news
        result = []
        for tag in tags_with_news:
            if News.published.filter(tags=tag).exists():
                result.append(tag)
        
        return result
    
    def lastmod(self, obj):
        """Return the last modification date of the most recent news with this tag"""
        latest_news = News.published.filter(tags=obj).order_by('-updated_at').first()
        if latest_news:
            return latest_news.updated_at
        return timezone.now()
    
    def location(self, obj):
        """Return the URL for the tag in format /topic/{tag-name}"""
        # Use raw tag name without quote() to allow custom view to handle encoding
        tag_name = obj.name.replace(' ', '-') if obj.name else ''
        return f'/topic/{tag_name}'


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        """Return all categories that have news"""
        # Only include categories that have published news
        categories_with_news = Category.objects.filter(
            news__isnull=False
        ).distinct()
        
        # Filter to only those with published news
        result = []
        for category in categories_with_news:
            if News.published.filter(category=category).exists():
                result.append(category)
        
        return result
    
    def lastmod(self, obj):
        """Return the last modification date of the most recent news in this category"""
        latest_news = News.published.filter(category=obj).order_by('-updated_at').first()
        if latest_news:
            return latest_news.updated_at
        return timezone.now()
    
    def location(self, obj):
        """Return the URL for the category"""
        # Since categories don't have direct URLs, we'll use a search/filter URL
        # You may need to adjust this based on your actual category URL structure
        # For now, using a query parameter format
        from urllib.parse import quote
        category_name = quote(obj.name) if obj.name else ''
        return f'/news/?category={category_name}'

