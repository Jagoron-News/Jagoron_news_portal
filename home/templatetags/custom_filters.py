from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.filter(is_safe=True)
def clean_rich_text(value):
    if not value:
        return ''
    
    soup = BeautifulSoup(value, 'html.parser')
    
    for tag in soup.find_all(True):
        if 'style' in tag.attrs:
            del tag.attrs['style']
            
        if tag.name == 'div':
            tag.name = 'p'
    
    return str(soup)



@register.filter
def to_bengali(value):
    bengali_digits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯']
    value_str = str(value)
    bengali_value = ''.join([bengali_digits[int(digit)] for digit in value_str if digit.isdigit()])
    return bengali_value


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)


@register.filter
def is_active_nav(nav_item, request):
    """
    Check if a nav item is active based on current URL
    Supports both old format (?section=X) and new format (/slug/)
    """
    if not request:
        return False
    
    # Check old format: query parameter
    section_id = request.GET.get('section')
    if section_id and str(nav_item.id) == str(section_id):
        return True
    
    # Check new format: slug-based URL
    current_path = request.path.rstrip('/')
    nav_slug = nav_item.get_slug()
    
    if nav_slug:
        # Normalize paths for comparison (remove trailing slashes)
        nav_url = nav_item.get_absolute_url().rstrip('/')
        
        # Check if current path exactly matches the nav's URL
        if current_path == nav_url:
            return True
        
        # Check if current path starts with the nav's slug followed by /
        # This handles subsections like /national/politics/
        if current_path.startswith(f'/{nav_slug}/'):
            return True
        
        # Also check if current path is exactly /nav_slug (without trailing slash)
        if current_path == f'/{nav_slug}':
            return True
    
    return False


@register.filter
def is_active_subsection(subsection, request):
    """
    Check if a subsection is active based on current URL
    Supports both old format (?sub_section=X) and new format (/section-slug/subsection-slug/)
    """
    if not request:
        return False
    
    # Check old format: query parameter
    subsection_id = request.GET.get('sub_section')
    if subsection_id and str(subsection.id) == str(subsection_id):
        return True
    
    # Check new format: slug-based URL
    current_path = request.path.rstrip('/')  # Remove trailing slash for comparison
    subsection_slug = subsection.get_slug()
    
    if subsection_slug and subsection.section:
        section_slug = subsection.section.get_slug()
        
        if section_slug:
            # Check if current path matches the subsection's full URL
            # Format: /section-slug/subsection-slug (without trailing slash after rstrip)
            expected_path = f'/{section_slug}/{subsection_slug}'
            if current_path == expected_path:
                return True
    
    return False
