from django.contrib import admin
from django.utils.html import format_html

from home.models import *

# Register your models here.

# SEO Inline Admin for Sections
class SectionSEOInline(admin.StackedInline):
    model = SectionSEO
    fieldsets = (
        ('Basic Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_author'),
            'description': 'Basic SEO meta tags for search engines'
        }),
        ('Canonical URL', {
            'fields': ('canonical_url',),
            'description': 'Canonical URL helps prevent duplicate content issues. Leave blank to use current URL.'
        }),
        ('Open Graph Tags', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_type', 'og_site_name'),
            'description': 'Open Graph tags for social media sharing (Facebook, LinkedIn, etc.)'
        }),
        ('Twitter Card Tags', {
            'fields': ('twitter_card', 'twitter_title', 'twitter_description', 'twitter_image'),
            'description': 'Twitter Card tags for Twitter sharing'
        }),
    )
    extra = 0
    max_num = 1
    can_delete = False

# SEO Inline Admin for SubSections
class SubSectionSEOInline(admin.StackedInline):
    model = SubSectionSEO
    fieldsets = (
        ('Basic Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_author'),
            'description': 'Basic SEO meta tags for search engines'
        }),
        ('Canonical URL', {
            'fields': ('canonical_url',),
            'description': 'Canonical URL helps prevent duplicate content issues. Leave blank to use current URL.'
        }),
        ('Open Graph Tags', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_type', 'og_site_name'),
            'description': 'Open Graph tags for social media sharing (Facebook, LinkedIn, etc.)'
        }),
        ('Twitter Card Tags', {
            'fields': ('twitter_card', 'twitter_title', 'twitter_description', 'twitter_image'),
            'description': 'Twitter Card tags for Twitter sharing'
        }),
    )
    extra = 0
    max_num = 1
    can_delete = False

@admin.register(NavbarItem)
class NavbarItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'position', 'is_active')  
    list_editable = ('position', 'is_active')  
    ordering = ('position',)  
    list_per_page = 20  
    search_fields = ('title', 'link')
    list_filter = ('is_active',)
    inlines = [SectionSEOInline]

    
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(NewsView)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_views', 'get_publish_status', 'created_by', 'created_at', 'scheduled_publish_at', 'updated_by', 'updated_at')
    list_filter = ('scheduled_publish_at', 'created_at', 'created_by')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Content', {
            'fields': ('section', 'sub_section', 'category', 'tags', 'top_sub_title', 'title', 'sub_title', 'sub_content', 'news_content')
        }),
        ('Images', {
            'fields': ('heading_image', 'heading_image_title', 'main_image', 'main_image_title')
        }),
        ('Metadata', {
            'fields': ('reporter', 'created_by', 'updated_by', 'created_at', 'updated_at')
        }),
        ('Publishing', {
            'fields': ('scheduled_publish_at',),
            'description': 'Leave empty to publish immediately, or set a future date/time to schedule publication.'
        }),
    )

    def get_views(self, obj):
        return obj.views.count if hasattr(obj, 'views') else 0
    get_views.short_description = 'Views'
    
    def get_publish_status(self, obj):
        if obj.is_scheduled:
            from django.utils import timezone
            return f"⏰ Scheduled ({obj.scheduled_publish_at.strftime('%Y-%m-%d %H:%M')})"
        elif obj.is_published:
            return "✅ Published"
        else:
            return "❌ Not Published"
    get_publish_status.short_description = 'Status'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
        return self.readonly_fields + readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            # If updating, preserve existing images if no new ones were uploaded
            old_obj = News.objects.get(pk=obj.pk)
            
            # Check if heading_image field was cleared or not provided
            if 'heading_image' in form.changed_data:
                # Field was in the form, check if it has a value
                if not form.cleaned_data.get('heading_image'):
                    # No new image, preserve the old one
                    obj.heading_image = old_obj.heading_image
            else:
                # Field not in form data, preserve the old one
                obj.heading_image = old_obj.heading_image
            
            # Check if main_image field was cleared or not provided
            if 'main_image' in form.changed_data:
                # Field was in the form, check if it has a value
                if not form.cleaned_data.get('main_image'):
                    # No new image, preserve the old one
                    obj.main_image = old_obj.main_image
            else:
                # Field not in form data, preserve the old one
                obj.main_image = old_obj.main_image
        
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()

    class Media:
        js = ('js/news_admin.js',)

# SEO Inline Admin for News
class NewsSEOInline(admin.StackedInline):
    model = NewsSEO
    fieldsets = (
        ('Basic Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_author'),
            'description': 'Basic SEO meta tags for search engines'
        }),
        ('Canonical URL', {
            'fields': ('canonical_url',),
            'description': 'Canonical URL helps prevent duplicate content issues. Leave blank to use current URL.'
        }),
        ('Open Graph Tags', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_type', 'og_site_name'),
            'description': 'Open Graph tags for social media sharing (Facebook, LinkedIn, etc.)'
        }),
        ('Twitter Card Tags', {
            'fields': ('twitter_card', 'twitter_title', 'twitter_description', 'twitter_image'),
            'description': 'Twitter Card tags for Twitter sharing'
        }),
    )
    extra = 0
    max_num = 1
    can_delete = False


# Update NewsAdmin to include SEO inline
NewsAdmin.inlines = [NewsSEOInline]


# SEO Inline Admin for Default Pages
class PageSEOInline(admin.StackedInline):
    model = PageSEO
    fieldsets = (
        ('Basic Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_author'),
            'description': 'Basic SEO meta tags for search engines'
        }),
        ('Canonical URL', {
            'fields': ('canonical_url',),
            'description': 'Canonical URL helps prevent duplicate content issues. Leave blank to use current URL.'
        }),
        ('Open Graph Tags', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_type', 'og_site_name'),
            'description': 'Open Graph tags for social media sharing (Facebook, LinkedIn, etc.)'
        }),
        ('Twitter Card Tags', {
            'fields': ('twitter_card', 'twitter_title', 'twitter_description', 'twitter_image'),
            'description': 'Twitter Card tags for Twitter sharing'
        }),
    )
    extra = 0
    max_num = 1
    can_delete = False


# Update Default_pages admin
@admin.register(Default_pages)
class DefaultPagesAdmin(admin.ModelAdmin):
    inlines = [PageSEOInline]
    list_display = ('title', 'link')
    search_fields = ('title', 'link')


@admin.register(URLRedirection)
class URLRedirectionAdmin(admin.ModelAdmin):
    list_display = ('old_url', 'new_url', 'redirect_type', 'is_active', 'created_at')
    list_filter = ('redirect_type', 'is_active', 'created_at')
    search_fields = ('old_url', 'new_url')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Redirection Details', {
            'fields': ('old_url', 'new_url', 'redirect_type', 'is_active'),
            'description': 'Configure URL redirections. Use 301 for permanent redirects (SEO-friendly) or 302 for temporary redirects.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(News, NewsAdmin)
admin.site.register(SiteInfo)



admin.site.site_header = "Jagoron News Panel"
admin.site.site_title = "Jagoron News Admin" 
admin.site.index_title = "Welcome to Jagoron News"

admin.site.register(VideoPost)

@admin.register(SubSection)
class SubSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'position', 'is_active')
    list_filter = ('section', 'is_active')
    search_fields = ('title',)
    ordering = ('section', 'position')
    inlines = [SubSectionSEOInline]

admin.site.register(SpecialNewTitle)
admin.site.register(SpecialNewSection)
admin.site.register(NewsReaction)
admin.site.register(Review)

# Register SEO models separately (they're also available via inlines)
admin.site.register(NewsSEO)
admin.site.register(PageSEO)
admin.site.register(SectionSEO)
admin.site.register(SubSectionSEO)


# SEO Manager - Robots.txt Admin
@admin.register(RobotsTxt)
class RobotsTxtAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'updated_at', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at', 'help_text_display')
    
    fieldsets = (
        ('Robots.txt Content', {
            'fields': ('content', 'is_active', 'help_text_display'),
            'description': '''
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0;">📝 How to create a robots.txt file:</h3>
                    <ul style="margin-bottom: 15px;">
                        <li><strong>User-agent:</strong> Specifies the crawler (e.g., *, Googlebot, Bingbot)</li>
                        <li><strong>Disallow:</strong> Blocks crawling of a path (e.g., /admin/, /private/)</li>
                        <li><strong>Allow:</strong> Allows crawling of a path (e.g., /public/)</li>
                        <li><strong>Sitemap:</strong> Specifies sitemap URL (e.g., https://jagoronnews.com/sitemap.xml)</li>
                    </ul>
                    <h4>📋 Recommended Example:</h4>
                    <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 3px; overflow-x: auto;">User-agent: *
Disallow: /admin/
Disallow: /jag-admin/
Disallow: /ckeditor/
Disallow: /static/admin/
Sitemap: https://jagoronnews.com/sitemap.xml</pre>
                    <p style="margin-top: 15px; margin-bottom: 0;"><strong>⚠️ Note:</strong> Only one robots.txt can be active at a time. When you save an active robots.txt, all others will be deactivated automatically.</p>
                </div>
            '''
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def help_text_display(self, obj):
        """Display helpful information"""
        if obj and obj.pk:
            return format_html(
                '<div style="background: #e7f3ff; padding: 10px; border-left: 4px solid #2196F3; margin-top: 10px;">'
                '<strong>💡 Tip:</strong> Your robots.txt will be accessible at '
                '<a href="/robots.txt" target="_blank">/robots.txt</a> once saved and activated.'
                '</div>'
            )
        return format_html(
            '<div style="background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-top: 10px;">'
            '<strong>ℹ️ Info:</strong> After saving, your robots.txt will be accessible at /robots.txt'
            '</div>'
        )
    help_text_display.short_description = 'Information'
    
    def save_model(self, request, obj, form, change):
        # Ensure only one active robots.txt
        if obj.is_active:
            RobotsTxt.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(AuthorCategory)
class AuthorCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(AuthorRole)
class AuthorRoleAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    list_display = ("title", "category", "priority")
    list_filter = ("category",)
    ordering = ("category", "priority")


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

