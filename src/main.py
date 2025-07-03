import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from .analysis.seo_analyzer import SEOAnalyzer
from .core.config import Config
from .core.logger import Logger
from .core.exceptions import ConfigurationError, NetworkError, APIError, handle_exception

def display_summary(result):
    if not result or 'seo_analysis_results' not in result:
        Logger.error("Analysis result not found!")
        return
    
    analysis = result['seo_analysis_results']
    website_info = result.get('website_info', {})
    
    print("\n" + "=" * 60)
    print("📋 SEO ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"🌐 Website: {website_info.get('url', 'N/A')}")
    print(f"🏷️  Title: {website_info.get('title', 'N/A')}")
    print(f"📝 Meta Description: {website_info.get('meta_description', 'N/A')}")
    
    print("\n📈 ANALYSIS RESULTS:")
    print(f"   📊 Overall Content Quality: {analysis.get('overall_content_quality_relevance', 'N/A')}")
    print(f"   🏗️  Heading Structure: {analysis.get('heading_structure_analysis', 'N/A')}")
    print(f"   🖼️  Image Optimization: {analysis.get('image_optimization_analysis', 'N/A')}")
    print(f"   🔗 Link Analysis: {analysis.get('linking_analysis', 'N/A')}")
    print(f"   📖 Readability: {analysis.get('readability_analysis', 'N/A')}")
    print(f"   ⚙️  Technical SEO: {analysis.get('technical_seo_notes', 'N/A')}")
    
    print("\n🎯 KEYWORD ANALYSIS:")
    keyword_analysis = analysis.get('keyword_analysis', {})
    primary_keywords = keyword_analysis.get('primary_keywords', [])
    secondary_keywords = keyword_analysis.get('secondary_keywords', [])
    print(f"   Primary: {', '.join(primary_keywords[:5]) if primary_keywords else 'N/A'}")
    print(f"   Secondary: {', '.join(secondary_keywords[:5]) if secondary_keywords else 'N/A'}")
    print(f"   Comment: {keyword_analysis.get('keyword_usage_comment', 'N/A')}")
    
    print("\n💡 RECOMMENDATIONS:")
    recommendations = analysis.get('actionable_recommendations', [])
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 60)

@handle_exception
def validate_environment():
    Logger.info("Validating configuration")
    try:
        config = Config()
        config.validate_config()
        Logger.info("Configuration validated successfully")
        return True
    except ConfigurationError as e:
        Logger.error(f"Configuration error: {str(e)}")
        print(f"❌ Configuration Error: {str(e)}")
        print("💡 Solution: Set OPENROUTER_API_KEY value in .env file")
        print("🔗 Get API Key: https://openrouter.ai")
        return False

@handle_exception
def analyze_domain_main(domain, args):
    Logger.info(f"Starting domain analysis: {domain}")
    
    try:
        analyzer = SEOAnalyzer()
        result = analyzer.analyze_domain(domain)
        
        if not result:
            Logger.error("Analysis could not be completed!")
            print("❌ Analysis could not be completed!")
            return False
        
        if args.verbose or args.summary_only:
            display_summary(result)
        
        if not args.summary_only:
            if args.output:
                filename = args.output
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_domain = domain.replace('.', '_').replace('/', '_')
                filename = f"seo_analysis_{safe_domain}_{timestamp}.json"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                Logger.info(f"Analysis saved to file: {filename}")
                print(f"\n✅ Analysis completed!")
                print(f"📄 Result file: {filename}")
            except Exception as e:
                Logger.error(f"File save error: {str(e)}")
                print(f"❌ File save error: {str(e)}")
                return False
        
        if result.get('seo_analysis_results', {}).get('overall_seo_score'):
            score = result['seo_analysis_results']['overall_seo_score']
            if score >= 80:
                print("🎉 Excellent! Your SEO score is very good.")
            elif score >= 60:
                print("👍 Good! Some improvements can be made.")
            elif score >= 40:
                print("⚠️  Average. Significant improvements needed.")
            else:
                print("🚨 Low score. Comprehensive SEO work required.")
        
        Logger.info(f"Domain analysis completed successfully: {domain}")
        return True
        
    except NetworkError as e:
        Logger.error(f"Network error: {str(e)}")
        print(f"❌ Network Error: {str(e)}")
        return False
    except APIError as e:
        Logger.error(f"API error: {str(e)}")
        print(f"❌ API Error: {str(e)}")
        return False
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False

def create_parser():
    parser = argparse.ArgumentParser(
        description='Comprehensive SEO Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Usage Examples:
  python -m src.main example.com
  python -m src.main -d google.com -o google_seo_analysis.json
  python -m src.main --domain facebook.com --summary-only
  python -m src.main -d linkedin.com -s --verbose

.env File Setup:
  1. Create .env file
  2. Add OPENROUTER_API_KEY=sk-or-v1-your-api-key
  3. Optional: Add OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
  
Getting API Key:
  1. Go to https://openrouter.ai
  2. Create an account
  3. Get your API key (starts with sk-or-v1-)
  4. Add to .env file as OPENROUTER_API_KEY
        '''
    )
    
    parser.add_argument(
        'domain',
        nargs='?',
        help='Domain to analyze (e.g., example.com)'
    )
    
    parser.add_argument(
        '-d', '--domain',
        help='Domain to analyze (alternative method)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file name (default: auto-generate)'
    )
    
    parser.add_argument(
        '-s', '--summary-only',
        action='store_true',
        help='Show summary only, don\'t create JSON file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Don\'t show startup banner'
    )
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.no_banner:
        print("=" * 60)
        print("🔍 COMPREHENSIVE SEO ANALYSIS TOOL")
        print("=" * 60)
        print("📊 Analyze your website's SEO performance in detail")
        print("🚀 Enhanced analysis powered by OpenRouter AI")
        print("=" * 60)
    
    domain = args.domain or args.domain
    if not domain:
        Logger.warning("Domain parameter not provided")
        print("❌ Error: Domain parameter required!")
        print("💡 Usage: python -m src.main example.com")
        print("📚 Help: python -m src.main --help")
        sys.exit(1)
    
    Logger.info(f"Program started, domain: {domain}")
    
    if not validate_environment():
        sys.exit(1)
    
    try:
        print(f"\n🔍 Starting analysis: {domain}")
        
        success = analyze_domain_main(domain, args)
        
        if success:
            Logger.info("Program completed successfully")
            sys.exit(0)
        else:
            Logger.error("Program ended with error")
            sys.exit(1)
            
    except KeyboardInterrupt:
        Logger.warning("Program stopped by user")
        print("\n⏹️  Analysis stopped by user.")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"Unexpected program error: {str(e)}")
        print(f"\n❌ Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 