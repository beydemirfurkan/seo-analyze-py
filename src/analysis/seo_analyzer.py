import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse, quote
import textstat
from collections import Counter
import math
from ..core.config import Config
from ..core.logger import Logger
from ..core.exceptions import NetworkError, ParsingError, APIError, ExceptionHandler, handle_exception
from .seo_schema import get_comprehensive_seo_schema

class SEOAnalyzer:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.USER_AGENT
        })
        Logger.info("SEOAnalyzer initialized")
    
    @handle_exception
    def normalize_url(self, domain):
        Logger.info(f"Normalizing URL: {domain}")
        if not domain.startswith(('http://', 'https://')):
            test_url = f"https://{domain}"
            try:
                response = self.session.head(test_url, timeout=10, allow_redirects=True)
                if response.status_code < 400:
                    Logger.info(f"HTTPS connection successful: {test_url}")
                    return test_url
            except:
                pass
            
            fallback_url = f"http://{domain}"
            Logger.warning(f"HTTPS failed, trying HTTP: {fallback_url}")
            return fallback_url
        return domain
    
    @handle_exception
    def scrape_and_parse_html(self, url):
        Logger.info(f"Fetching page content: {url}")
        try:
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            Logger.info(f"Page successfully fetched, size: {len(response.text)} characters")
            return BeautifulSoup(response.text, 'html.parser'), response
        except requests.exceptions.RequestException as e:
            ExceptionHandler.handle_network_error(url, e)
    
    @handle_exception
    def extract_social_media_tags(self, soup):
        Logger.info("Extracting social media tags")
        og_tags = {}
        twitter_tags = {}
        
        og_properties = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
        for prop in og_properties:
            tag = soup.find('meta', property=prop)
            if tag:
                og_tags[prop.replace(':', '_')] = tag.get('content', '')
        
        twitter_names = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
        for name in twitter_names:
            tag = soup.find('meta', attrs={'name': name})
            if tag:
                twitter_tags[name.replace(':', '_')] = tag.get('content', '')
        
        Logger.info(f"Social media tags extracted: OG={len(og_tags)}, Twitter={len(twitter_tags)}")
        return og_tags, twitter_tags
    
    @handle_exception
    def extract_structured_data(self, soup):
        Logger.info("Analyzing structured data")
        has_json_ld = len(soup.find_all('script', type='application/ld+json')) > 0
        has_microdata = len(soup.find_all(attrs={'itemtype': True})) > 0
        has_schema_org = has_json_ld or has_microdata
        
        Logger.info(f"Structured data analysis completed: Schema.org present: {has_schema_org}")
        return {
            'has_schema_org': has_schema_org,
            'has_json_ld': has_json_ld,
            'has_microdata': has_microdata
        }
    
    @handle_exception
    def calculate_readability_metrics(self, text):
        if not text.strip():
            return {
                'flesch_reading_ease': 0,
                'avg_words_per_sentence': 0,
                'complex_words_percentage': 0
            }
        
        try:
            flesch_score = textstat.flesch_reading_ease(text)
            avg_words = textstat.avg_sentence_length(text)
            
            words = re.findall(r'\b\w+\b', text.lower())
            complex_words = sum(1 for word in words if textstat.syllable_count(word) >= 3)
            complex_percentage = (complex_words / len(words)) * 100 if words else 0
            
            metrics = {
                'flesch_reading_ease': round(flesch_score, 2),
                'avg_words_per_sentence': round(avg_words, 2),
                'complex_words_percentage': round(complex_percentage, 2)
            }
            Logger.info(f"Readability metrics calculated: Flesch={metrics['flesch_reading_ease']}")
            return metrics
        except Exception as e:
            Logger.error(f"Readability calculation error: {e}")
            return {
                'flesch_reading_ease': 0,
                'avg_words_per_sentence': 0,
                'complex_words_percentage': 0
            }
    
    @handle_exception
    def analyze_technical_factors(self, soup, url=""):
        Logger.info("Analyzing technical SEO factors")
        technical_analysis = {
            'page_speed_factors': {
                'inline_styles_count': len(soup.find_all('style')),
                'inline_scripts_count': len(soup.find_all('script', src=False)),
                'external_stylesheets': len(soup.find_all('link', rel='stylesheet')),
                'external_scripts': len(soup.find_all('script', src=True)),
                'total_css_files': len(soup.find_all('link', rel='stylesheet')),
                'total_js_files': len(soup.find_all('script', src=True))
            },
            'mobile_optimization': {
                'has_viewport_meta': False,
                'viewport_content': '',
                'has_media_queries': False,
                'touch_friendly_elements': 0
            },
            'security_analysis': {
                'is_https': url.startswith('https://'),
                'mixed_content_issues': 0
            },
            'content_structure': {
                'has_forms': len(soup.find_all('form')) > 0,
                'forms_count': len(soup.find_all('form')),
                'has_tables': len(soup.find_all('table')) > 0,
                'tables_count': len(soup.find_all('table')),
                'lists_count': len(soup.find_all(['ul', 'ol'])),
                'has_breadcrumbs': False
            },
            'seo_technical': {
                'has_robots_meta': False,
                'robots_content': '',
                'has_sitemap_reference': False,
                'has_hreflang': len(soup.find_all('link', rel='alternate', hreflang=True)) > 0
            },
            'accessibility': {
                'images_without_alt': 0,
                'headings_structure_issues': [],
                'accessibility_score': 0
            }
        }
        
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_tag:
            technical_analysis['mobile_optimization']['has_viewport_meta'] = True
            technical_analysis['mobile_optimization']['viewport_content'] = viewport_tag.get('content', '')
        
        # Media queries kontrolü
        styles = soup.find_all('style')
        for style in styles:
            if style.string and '@media' in style.string:
                technical_analysis['mobile_optimization']['has_media_queries'] = True
                break
        
        # Touch friendly elements (buttons, inputs)
        touch_elements = soup.find_all(['button', 'input', 'select', 'textarea'])
        technical_analysis['mobile_optimization']['touch_friendly_elements'] = len(touch_elements)
        
        # Robots meta kontrol
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        if robots_tag:
            technical_analysis['seo_technical']['has_robots_meta'] = True
            technical_analysis['seo_technical']['robots_content'] = robots_tag.get('content', '')
        
        # Sitemap referansı kontrol (head içinde)
        sitemap_links = soup.find_all('link', type='application/xml')
        technical_analysis['seo_technical']['has_sitemap_reference'] = len(sitemap_links) > 0
        
        # Breadcrumb kontrol (schema.org BreadcrumbList)
        breadcrumb_scripts = soup.find_all('script', type='application/ld+json')
        for script in breadcrumb_scripts:
            try:
                if script.string and 'BreadcrumbList' in script.string:
                    technical_analysis['content_structure']['has_breadcrumbs'] = True
                    break
            except:
                pass
        
        images_without_alt = sum(1 for img in soup.find_all('img') if not img.get('alt') or not img.get('alt').strip())
        technical_analysis['accessibility']['images_without_alt'] = images_without_alt
        
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            technical_analysis['accessibility']['headings_structure_issues'].append('no-h1-tag')
        elif h1_count > 1:
            technical_analysis['accessibility']['headings_structure_issues'].append('multiple-h1-tags')
        
        accessibility_score = 100
        if images_without_alt > 0:
            accessibility_score -= min(images_without_alt * 5, 50)
        if technical_analysis['accessibility']['headings_structure_issues']:
            accessibility_score -= 20
        
        technical_analysis['accessibility']['accessibility_score'] = max(0, accessibility_score)
        
        Logger.info(f"Technical analysis completed: Accessibility score {accessibility_score}")
        return technical_analysis
    
    @handle_exception
    def preprocess_html_for_llm(self, url, soup, response):
        Logger.info("Preparing HTML data for LLM analysis")
        domain = urlparse(url).netloc
        
        title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"
        title_length = len(title) if title != "N/A" else 0
        
        meta_description_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description_tag['content'].strip() if meta_description_tag else "N/A"
        meta_description_length = len(meta_description) if meta_description != "N/A" else 0
        
        meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        meta_keywords = meta_keywords_tag['content'] if meta_keywords_tag else "N/A"
        
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        canonical_url = canonical_tag['href'] if canonical_tag else "N/A"
        
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        viewport_meta = viewport_tag['content'] if viewport_tag else "N/A"
        
        lang_attr = soup.find('html')
        lang_attribute = lang_attr.get('lang', 'N/A') if lang_attr else "N/A"
        
        charset_tag = soup.find('meta', attrs={'charset': True})
        charset = charset_tag['charset'] if charset_tag else "N/A"
        
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        robots_meta = robots_tag['content'] if robots_tag else "N/A"
        
        og_tags, twitter_tags = self.extract_social_media_tags(soup)
        structured_data = self.extract_structured_data(soup)
        
        headings = []
        heading_counts = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        
        for i in range(1, 7):
            for idx, heading in enumerate(soup.find_all(f'h{i}')):
                text = heading.get_text(strip=True)
                if text and len(headings) < self.config.MAX_HEADINGS:
                    headings.append({
                        'tag': f'h{i}',
                        'text': text[:100],
                        'position': idx + 1
                    })
                heading_counts[f'h{i}'] += 1
        
        heading_structure = {
            'h1_count': heading_counts['h1'],
            'h2_count': heading_counts['h2'],
            'h3_count': heading_counts['h3'],
            'h4_count': heading_counts['h4'],
            'h5_count': heading_counts['h5'],
            'h6_count': heading_counts['h6'],
            'total_headings': sum(heading_counts.values())
        }
        
        images_stats = {
            'total_images': 0,
            'images_without_alt': 0,
            'images_without_src': 0,
            'images_without_dimensions': 0
        }
        
        for img in soup.find_all('img'):
            images_stats['total_images'] += 1
            
            if not img.get('alt', '').strip():
                images_stats['images_without_alt'] += 1
            
            if not img.get('src', '').strip():
                images_stats['images_without_src'] += 1
            
            if not img.get('width') or not img.get('height'):
                images_stats['images_without_dimensions'] += 1
        
        links_stats = {
            'internal_links': 0,
            'external_links': 0,
            'nofollow_links': 0,
            'links_without_anchor_text': 0,
            'links_without_title': 0
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            if href.startswith(('http://', 'https://')):
                link_domain = urlparse(href).netloc
                is_internal = link_domain == domain
            else:
                is_internal = True
            
            if is_internal:
                links_stats['internal_links'] += 1
            else:
                links_stats['external_links'] += 1
            
            rel_attr = link.get('rel', [])
            if 'nofollow' in rel_attr:
                links_stats['nofollow_links'] += 1
            
            if not text.strip():
                links_stats['links_without_anchor_text'] += 1
            
            if not link.get('title', '').strip():
                links_stats['links_without_title'] += 1
        
        content_tags = soup.find_all(['p', 'div', 'article', 'section', 'main'])
        main_text = ' '.join([tag.get_text(strip=True) for tag in content_tags])
        main_text_snippet = main_text[:self.config.MAX_TEXT_LENGTH]
        
        paragraphs = soup.find_all('p')
        paragraph_count = len(paragraphs)
        
        sentences = re.split(r'[.!?]+', main_text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        words = re.findall(r'\b\w+\b', main_text)
        word_count_total = len(words)
        average_sentence_length = word_count_total / sentence_count if sentence_count > 0 else 0
        
        readability_metrics = self.calculate_readability_metrics(main_text)
        technical_analysis = self.analyze_technical_factors(soup, url)
        
        preprocessed_data = {
            "website_info": {
                "url": url,
                "domain": domain,
                "title": title,
                "title_length": title_length,
                "meta_description": meta_description,
                "meta_description_length": meta_description_length,
                "meta_keywords": meta_keywords,
                "canonical_url": canonical_url,
                "viewport_meta": viewport_meta,
                "lang_attribute": lang_attribute,
                "charset": charset,
                "robots_meta": robots_meta,
                "og_tags": og_tags,
                "twitter_tags": twitter_tags,
                "structured_data": structured_data
            },
            "seo_elements_extracted": {
                "headings": headings,
                "heading_structure": heading_structure,
                "images_stats": images_stats,
                "links_stats": links_stats,
                "main_text_snippet": main_text_snippet,
                "word_count_total": word_count_total,
                "paragraph_count": paragraph_count,
                "sentence_count": sentence_count,
                "average_sentence_length": round(average_sentence_length, 2),
                "readability_metrics": readability_metrics
            },
            "technical_seo_analysis": technical_analysis
        }
        
        Logger.info(f"HTML preprocessing completed: {word_count_total} words, {len(headings)} headings")
        return preprocessed_data
    
    @handle_exception
    def analyze_with_llm(self, preprocessed_data):
        Logger.info("Starting LLM SEO analysis")
        
        try:
            self.config.validate_config()
        except Exception as e:
            ExceptionHandler.handle_api_error("OpenRouter", f"Configuration error: {e}")
        
        headers = {
            'Authorization': f'Bearer {self.config.OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:3000',
            'X-Title': 'SEO Analyzer'
        }
        
        schema_prompt = json.dumps(get_comprehensive_seo_schema(), indent=2)
        
        prompt = f"""
You are a professional SEO expert analyzing a website. Based on the provided data, perform a comprehensive SEO audit and scoring.

Website Data:
{json.dumps(preprocessed_data, indent=2, ensure_ascii=False)}

JSON Schema (you MUST follow this exact structure):
{schema_prompt}

IMPORTANT INSTRUCTIONS:
1. YOU must determine the overall SEO score (0-100) based on your professional analysis
2. Score each category independently: Title/Meta, Content Quality, Technical SEO, Mobile, etc.
3. Provide specific, actionable recommendations based on real issues found
4. Analyze keyword usage patterns from the content
5. Evaluate technical factors: page speed, accessibility, mobile optimization
6. Consider content structure, readability, and user experience
7. Check for SEO best practices compliance

SCORING GUIDELINES:
- 90-100: Excellent SEO optimization
- 75-89: Good with minor improvements needed  
- 60-74: Average, several optimization opportunities
- 40-59: Poor, major SEO work required
- 0-39: Critical issues, complete SEO overhaul needed

Be thorough, professional, and base your analysis on the actual data provided. Return only valid JSON that matches the schema exactly.
"""
        
        data = {
            'model': self.config.LLM_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,
            'temperature': 0.3
        }
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                Logger.info(f"LLM API call attempt {attempt + 1}")
                response = requests.post(
                    self.config.get_api_url(),
                    headers=headers,
                    json=data,
                    timeout=60
                )
                
                if response.status_code == 429:
                    delay = min(self.config.INITIAL_DELAY * (2 ** attempt), 60)
                    Logger.warning(f"Rate limit hit, waiting {delay} seconds")
                    time.sleep(delay)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' not in result or not result['choices']:
                    raise APIError("No choices found in LLM response")
                
                content = result['choices'][0]['message']['content'].strip()
                
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                seo_analysis = json.loads(content)
                Logger.info("LLM analysis completed successfully")
                return seo_analysis
                
            except requests.exceptions.RequestException as e:
                Logger.error(f"API call error (attempt {attempt + 1}): {e}")
                if attempt == self.config.MAX_RETRIES - 1:
                    ExceptionHandler.handle_api_error("OpenRouter", str(e))
                time.sleep(min(self.config.INITIAL_DELAY * (attempt + 1), 30))
                
            except json.JSONDecodeError as e:
                Logger.error(f"JSON parsing error: {e}")
                if attempt == self.config.MAX_RETRIES - 1:
                    ExceptionHandler.handle_parsing_error("LLM Response JSON", str(e))
                time.sleep(min(self.config.INITIAL_DELAY * (attempt + 1), 30))
                
            except Exception as e:
                Logger.error(f"Unexpected LLM error: {e}")
                if attempt == self.config.MAX_RETRIES - 1:
                    ExceptionHandler.handle_api_error("OpenRouter", str(e))
                time.sleep(min(self.config.INITIAL_DELAY * (attempt + 1), 30))
    
    
    @handle_exception
    def analyze_domain(self, domain):
        Logger.info(f"Starting domain analysis: {domain}")
        
        normalized_url = self.normalize_url(domain)
        
        soup, response = self.scrape_and_parse_html(normalized_url)
        if not soup:
            Logger.error("Could not fetch HTML content")
            return None
        
        preprocessed_data = self.preprocess_html_for_llm(normalized_url, soup, response)
        
        seo_analysis_results = self.analyze_with_llm(preprocessed_data)
        
        final_result = {
            **preprocessed_data,
            "seo_analysis_results": seo_analysis_results
        }
        
        Logger.info(f"Domain analysis completed: {domain}")
        return final_result 