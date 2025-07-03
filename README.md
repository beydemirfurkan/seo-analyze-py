# 🔍 Comprehensive SEO Analysis Tool

Comprehensive SEO analysis tool powered by OpenRouter AI. Analyzes the SEO performance of your websites in detail and provides actionable recommendations.

## ✨ Features

### 🎯 Comprehensive SEO Analysis
- **Technical SEO**: Page speed, mobile compatibility, accessibility
- **Content Analysis**: Keyword optimization, readability
- **Structural Analysis**: HTML structure, heading hierarchy, meta tags
- **Link Analysis**: Internal and external links, anchor text optimization
- **Image Optimization**: Alt text, file sizes
- **Social Media**: Open Graph, Twitter Card optimization
- **Structured Data**: Schema.org, JSON-LD analysis

### 🤖 AI-Powered Analysis
- Enhanced analysis with OpenRouter API
- Smart recommendation system
- Priority-based improvement suggestions

### 🛠️ Flexible Usage
- **Command Line**: Quick one-time analyses
- **API Server**: Integration and batch processing
- **Asynchronous Processing**: Background analysis for large sites

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/seo-analyzer.git
cd seo-analyzer
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
cp .env.example .env
# Edit the .env file and enter your API key
```

**.env file example:**
```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

## 📖 Usage

### 🖥️ Command Line Usage

#### Basic Usage
```bash
python run.py example.com
# or
python -m src.main example.com
```

#### Customized Analysis
```bash
# Specify output file
python run.py -d google.com -o google_analysis.json

# Show summary only
python run.py --domain facebook.com --summary-only

# Detailed output
python run.py -d linkedin.com --verbose
```

#### Command Line Parameters
```
positional arguments:
  domain                Domain to analyze (e.g., example.com)

options:
  -h, --help            Show this help message
  -d, --domain DOMAIN   Domain to analyze (alternative method)
  -o, --output OUTPUT   Output file name
  -s, --summary-only    Show summary only
  -v, --verbose         Show detailed output
  --no-banner          Don't show startup banner
```

### 🌐 API Server Usage

#### Start the Server
```bash
python run_api.py
# or
python -m src.api.server
```

#### API Endpoints

**Health Check**
```bash
curl http://localhost:5000/health
```

**Synchronous Analysis (for small sites)**
```bash
curl -X POST http://localhost:5000/analyze-sync \
     -H "Content-Type: application/json" \
     -d '{"domain": "example.com"}'
```

**Asynchronous Analysis (for large sites)**
```bash
# Start analysis
curl -X POST http://localhost:5000/analyze \
     -H "Content-Type: application/json" \
     -d '{"domain": "example.com"}'

# Check status
curl http://localhost:5000/status/analysis_id

# Get result
curl http://localhost:5000/result/analysis_id
```

**List All Analyses**
```bash
curl http://localhost:5000/list-analyses
```

## 📊 Output Format

### JSON Structure
```json
{
  "website_info": {
    "url": "https://example.com",
    "domain": "example.com",
    "title": "Example Domain",
    "title_length": 14,
    "meta_description": "This domain is for use in examples...",
    "og_tags": { ... },
    "twitter_tags": { ... }
  },
  "seo_elements_extracted": {
    "headings": [ ... ],
    "images": [ ... ],
    "links": [ ... ],
    "word_count_total": 150,
    "readability_metrics": { ... }
  },
  "technical_seo_analysis": {
    "page_speed_factors": { ... },
    "mobile_optimization": { ... },
    "accessibility": { ... }
  },
  "seo_analysis_results": {
    "overall_seo_score": 75,
    "keyword_analysis": { ... },
    "title_tag_analysis": { ... },
    "actionable_recommendations": [ ... ]
  }
}
```

### Scoring System
- **90-100**: Excellent
- **80-89**: Very Good
- **70-79**: Good
- **60-69**: Average
- **50-59**: Poor
- **0-49**: Critical

## 🔧 Configuration

### config.py Settings
```python
class Config:
    # API Settings
    OPENROUTER_API_KEY = "your-key-here"
    LLM_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
    
    # Scraping Limits
    MAX_TEXT_LENGTH = 8000
    MAX_HEADINGS = 20
    MAX_IMAGES = 20
    MAX_LINKS = 25
    
    # SEO Thresholds
    MIN_TITLE_LENGTH = 30
    MAX_TITLE_LENGTH = 60
    MIN_META_DESC_LENGTH = 120
    MAX_META_DESC_LENGTH = 160
```

## 🚀 API Examples

### Synchronous Analysis
```python
import requests

response = requests.post('http://localhost:5000/analyze-sync', 
                        json={'domain': 'example.com'})
result = response.json()
print(f"SEO Score: {result['result']['seo_analysis_results']['overall_seo_score']}")
```

### Asynchronous Analysis
```python
import requests
import time

# Start analysis
response = requests.post('http://localhost:5000/analyze', 
                        json={'domain': 'example.com'})
analysis_id = response.json()['analysis_id']

# Check status
while True:
    status_response = requests.get(f'http://localhost:5000/status/{analysis_id}')
    status = status_response.json()
    
    if status['status'] == 'completed':
        # Get results
        result_response = requests.get(f'http://localhost:5000/result/{analysis_id}')
        result = result_response.json()
        break
    elif status['status'] == 'failed':
        print(f"Analysis failed: {status['message']}")
        break
    
    print(f"Progress: {status['progress']}%")
    time.sleep(5)
```

## 📝 Development

### Project Structure
```
seo-analyzer/
├── src/
│   ├── analysis/         # SEO analysis logic
│   ├── api/             # Flask API server
│   ├── core/            # Core utilities
│   └── main.py          # CLI entry point
├── logs/                # Log files
├── run.py              # CLI runner
├── run_api.py          # API runner
└── requirements.txt    # Dependencies
```

### Adding New Features
1. Create feature branch
2. Add tests
3. Update documentation
4. Submit pull request

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [documentation](#usage)
2. Search [existing issues](https://github.com/your-username/seo-analyzer/issues)
3. Create a [new issue](https://github.com/your-username/seo-analyzer/issues/new)

## 🔗 Related Projects

- [OpenRouter API](https://openrouter.ai/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Flask](https://flask.palletsprojects.com/)

---

Made with ❤️ by [Your Name](https://github.com/your-username)