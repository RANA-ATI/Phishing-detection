import pandas as pd
from urllib.parse import urlparse
import re
import joblib
import requests
from bs4 import BeautifulSoup
import urllib.request


def count_sensitive_words(text):
    # Implement logic to count sensitive words in the text
    # For example:
    sensitive_words = [
    'password',
    'credit card',
    'social security number',
    'bank account',
    'personal identification number',
    'PIN',
    'mother\'s maiden name',
    'date of birth',
    'security code',
    'CVV',
    'passport number',
    'driver\'s license number',
    'address',
    'phone number',
    'email address',
    'username',
    'account number',
    'income',
    'ethnicity',
    'nationality',
    'religion',
    'sexual orientation',
    'gender identity',
    'disability',
    'medical condition',
    'political affiliation',
    'criminal record',
    'marital status',
    'child custody',
    'alimony',
    'tax return',
    'voting history',
    'trade secret',
    'confidential',
    'privileged',
    'restricted',
    'classified',
    'top secret'
]
    count = sum(1 for word in sensitive_words if word in text)
    return count

def check_for_brand_name(soup):
    # Implement logic to check for an embedded brand name in the HTML content
    # For example:
    brand_names = [
        'Acme Corporation', 'WidgetWorks', 'Gizmo Global', 'TechTrend', 'InnovateIQ',
        'ElectroElite', 'MaxTech', 'VitaVibe', 'AquaFresh', 'LuxorLux', 'EcoEssentials',
        'BioBlend', 'GloGenix', 'FlexiTech', 'MegaMart', 'UrbanEdge', 'StyleSpot',
        'NovaNow', 'PulsePoint', 'GigaGlow', 'PurePlus', 'EverEco', 'TrueTrend',
        'EpicEssence', 'PowerPulse', 'VitalVogue', 'GloGlobal', 'PrimePulse', 'TrendTech',
        'LuxeLife', 'Apple', 'Microsoft', 'Amazon', 'Google', 'Facebook', 'Tesla',
        'Walmart', 'Berkshire Hathaway', 'Johnson & Johnson', 'JPMorgan Chase', 'Visa',
        'Procter & Gamble', 'Intel', 'Verizon', 'AT&T', 'Walt Disney', 'Mastercard',
        'Cisco', 'McDonald\'s', 'Coca-Cola', 'Nestle', 'Toyota', 'Samsung', 'IBM',
        'Netflix', 'Adobe', 'Nike', 'Sony', 'General Electric', 'Exxon Mobil'
    ]

    for brand_name in brand_names:
        if brand_name.lower() in soup.text.lower():
            return 1
    
    return 0

def calculate_external_links(soup):
    # Implement logic to calculate the percentage of external hyperlinks
    total_links = len(soup.find_all('a'))
    ext_links = sum(1 for link in soup.find_all('a') if 'http' in link.get('href', ''))
    return ext_links / total_links if total_links != 0 else 0

def calculate_external_resource_urls(soup):
    # Implement logic to calculate the percentage of external resource URLs
    # External resource URLs include images, scripts, stylesheets, etc.
    # For example:
    total_urls = len(soup.find_all(['img', 'script', 'link']))
    ext_urls = sum(1 for url in soup.find_all(['img', 'script', 'link']) if 'http' in url.get('src', '') or 'http' in url.get('href', ''))
    return ext_urls / total_urls if total_urls != 0 else 0

def has_external_favicon(soup):
    # Implement logic to check if the webpage has an external favicon link
    favicon = soup.find('link', rel='icon')
    if favicon:
        href = favicon.get('href', '')
        return 1 if 'http' in href else 0
    return 0

def has_insecure_forms(soup):
    # Implement logic to check if there are insecure forms (submit data over HTTP)
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if action.startswith('http://'):
            return 1
    return 0

def has_relative_form_action(soup):
    # Check if any form action is relative
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if not action.startswith('http'):
            return 1
    return 0

def has_external_form_action(soup):
    # Check if any form action is external
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if 'http' in action:
            return 1
    return 0

def has_abnormal_form_action(soup):
    # Check if any form action is abnormal (e.g., javascript)
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if action.startswith('javascript'):
            return 1
    return 0

def calculate_null_self_redirect_hyperlinks(soup):
    # Calculate the percentage of hyperlinks with null or self redirection
    total_links = len(soup.find_all('a'))
    null_or_self_redirect_links = sum(1 for link in soup.find_all('a') if is_null_or_self_redirect(link))
    return null_or_self_redirect_links / total_links if total_links != 0 else 0

def is_null_or_self_redirect(link):
    href = link.get('href', '')
    if not href or href == '#' or href == '' or href == '/':
        return True
    elif href.startswith('http') and urlparse(href).netloc == urlparse(link.get('href', '')).netloc:
        return True
    return False

def has_frequent_domain_name_mismatch(soup, url):
    # Check if there are frequent domain name mismatches in hyperlinks
    total_links = len(soup.find_all('a'))
    domain_name_mismatch_links = sum(1 for link in soup.find_all('a') if has_domain_name_mismatch(link, url))
    return 1 if domain_name_mismatch_links / total_links >= 0.5 else 0

def has_frequent_domain_name_mismatch(soup, url):
    # Check if there are frequent domain name mismatches in hyperlinks
    total_links = len(soup.find_all('a'))
    if total_links == 0:
        return 0
    else:
        domain_name_mismatch_links = sum(1 for link in soup.find_all('a') if has_domain_name_mismatch(link, url))
        return 1 if domain_name_mismatch_links / total_links >= 0.5 else 0
    
def has_domain_name_mismatch(link, url):
    href = link.get('href', '')
    if href.startswith('http') and urlparse(href).netloc != urlparse(url).netloc:
        return True
    return False

def check_submit_info_to_email(soup):
    # Implement logic to check if the form submits information to an email
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if 'mailto:' in action:
            return 1
    return 0

def check_iframe_or_frame(soup):
    # Implement logic to check if the webpage contains iframes or frames
    if soup.find('iframe') or soup.find('frame'):
        return 1
    return 0

def check_missing_title(soup):
    # Implement logic to check if the webpage is missing a title tag
    if not soup.title:
        return 1
    return 0

def check_images_only_in_form(soup):
    # Implement logic to check if images are only present within form elements
    images = soup.find_all('img')
    forms = soup.find_all('form')
    if len(images) > 0:
        for image in images:
            if image.find_parent('form') is None:
                return 0
        return 1
    return 0

def calculate_subdomain_level_rt(url):
    # Implement logic to calculate the subdomain level ratio
    parsed_url = urlparse(url)
    subdomains = parsed_url.netloc.split('.')
    if len(subdomains) > 2:
        return 1
    elif len(subdomains) == 2:
        return 0
    else:
        return -1
    
def check_url_length(html_content):
    # Implement logic to check URL length
    url_length = len(html_content)
    return 1 if url_length > 255 else 0 if 150 <= url_length <= 255 else -1

def check_pct_ext_resource_urls(soup):
    # Implement logic to check the percentage of external resource URLs
    total_urls = len(soup.find_all(['img', 'script', 'link']))
    ext_urls = sum(1 for url in soup.find_all(['img', 'script', 'link']) if 'http' in url.get('src', '') or 'http' in url.get('href', ''))
    pct_ext_resource_urls = ext_urls / total_urls if total_urls != 0 else 0
    return 1 if pct_ext_resource_urls > 0.5 else -1 if pct_ext_resource_urls > 0.2 else 0

def check_abnormal_ext_form_action(soup):
    # Implement logic to check abnormal external form action
    forms = soup.find_all('form')
    abnormal_forms = sum(1 for form in forms if 'http' in form.get('action', ''))
    return 1 if abnormal_forms > 0 else 0

def check_ext_meta_script_link(soup):
    # Implement logic to check external meta, script, or link tags
    ext_tags = sum(1 for tag in soup.find_all(['meta', 'script', 'link']) if tag.get('src') or tag.get('href'))
    return 1 if ext_tags > 0 else 0

def check_pct_ext_null_self_redirect_hyperlinks(soup):
    # Implement logic to check the percentage of external null self-redirect hyperlinks
    ext_null_self_redirect_links = sum(1 for link in soup.find_all('a') if link.get('href') == '#' or link.get('href') == 'javascript:void(0)')
    total_links = len(soup.find_all('a'))
    pct_ext_null_self_redirect_hyperlinks = ext_null_self_redirect_links / total_links if total_links != 0 else 0
    return 1 if pct_ext_null_self_redirect_hyperlinks > 0.5 else -1 if pct_ext_null_self_redirect_hyperlinks > 0.2 else 0

def extract_features(url):

    def parse_html_content(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check for fake links in the status bar
        fake_links = sum(1 for link in soup.find_all('a') if 'javascript' in link.get('href', '').lower())
        fake_link_in_status_bar = 1 if fake_links > 0 else 0
        
        # Check if right-click is disabled
        right_click_disabled = 1 if 'contextmenu' in html_content.decode().lower() else 0
        
        # Check for pop-up windows
        pop_up_windows = sum(1 for tag in soup.find_all() if tag.get('onload') and 'window.open' in tag.get('onload').lower())
        pop_up_window = 1 if pop_up_windows > 0 else 0

        return fake_link_in_status_bar, right_click_disabled, pop_up_window

def extract_features(url):
    try:
        # Fetch the webpage content
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to fetch URL:", response.status_code)
            return "This site is inaccessible, making it difficult to classify it appropriately"

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        parsed_url = urlparse(url)
        num_dots = url.count('.')
        subdomain_level = len(parsed_url.netloc.split('.')) - 1
        path_level = url.count('/') - 1
        url_length = len(url)
        num_dash = url.count('-')
        num_dash_in_hostname = parsed_url.netloc.count('-')
        at_symbol = 1 if '@' in parsed_url.netloc else 0
        tilde_symbol = 1 if '~' in url else 0
        num_underscore = url.count('_')
        num_percent = url.count('%')
        num_query_components = len(parsed_url.query.split('&'))
        num_ampersand = url.count('&')
        num_hash = url.count('#')
        num_numeric_chars = sum(c.isdigit() for c in url)
        no_https = 1 if not url.startswith('https://') else 0
        random_string = 1 if re.search(r'\b\d{5,}\b', url) else 0
        ip_address = 1 if re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', parsed_url.netloc) else 0
        domain_in_subdomains = 1 if '.' in parsed_url.netloc[:-4] else 0
        domain_in_paths = 1 if '.' in parsed_url.path else 0
        https_in_hostname = 1 if 'https' in parsed_url.netloc else 0
        hostname_length = len(parsed_url.netloc)
        path_length = len(parsed_url.path)
        query_length = len(parsed_url.query)
        double_slash_in_path = url.count('//')

        # Feature extraction
        num_sensitive_words = count_sensitive_words(html_content)
        embedded_brand_name = check_for_brand_name(soup)
        pct_ext_hyperlinks = calculate_external_links(soup)
        pct_ext_resource_urls = calculate_external_resource_urls(soup)
        ext_favicon = has_external_favicon(soup)
        insecure_forms = has_insecure_forms(soup)

        relative_form_action = has_relative_form_action(soup)
        ext_form_action = has_external_form_action(soup)
        abnormal_form_action = has_abnormal_form_action(soup)
        pct_null_self_redirect_hyperlinks = calculate_null_self_redirect_hyperlinks(soup)
        frequent_domain_name_mismatch = has_frequent_domain_name_mismatch(soup, url)

        submit_info_to_email = check_submit_info_to_email(soup)
        iframe_or_frame = check_iframe_or_frame(soup)
        missing_title = check_missing_title(soup)
        images_only_in_form = check_images_only_in_form(soup)
        subdomain_level_rt = calculate_subdomain_level_rt(url)

        url_length_rt = check_url_length(html_content)
        pct_ext_resource_urls_rt = check_pct_ext_resource_urls(soup)
        abnormal_ext_form_action_r = check_abnormal_ext_form_action(soup)
        ext_meta_script_link_rt = check_ext_meta_script_link(soup)
        pct_ext_null_self_redirect_hyperlinks_rt = check_pct_ext_null_self_redirect_hyperlinks(soup)

        features = [
            pct_null_self_redirect_hyperlinks, frequent_domain_name_mismatch, num_dash, 
            submit_info_to_email, pct_ext_hyperlinks, insecure_forms, num_dots, 
            pct_ext_hyperlinks, num_sensitive_words
        ]

        rfc_model = joblib.load("models/best_model.pkl")

        # Make predictions
        prediction = rfc_model.predict([features])

        if prediction[0] == 0:
            prediction = "Legitimate"
        else:
            prediction = "Phishing"

        return prediction

    except Exception as e:
        print("Error:", e)
        return "This site is inaccessible, making it difficult to classify it appropriately"
