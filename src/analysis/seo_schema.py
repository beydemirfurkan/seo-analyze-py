def get_comprehensive_seo_schema():
    return {
        "website_info": {
            "url": "string",
            "domain": "string",
            "title": "string",
            "title_length": "integer",
            "meta_description": "string",
            "meta_description_length": "integer",
            "meta_keywords": "string",
            "canonical_url": "string",
            "viewport_meta": "string",
            "lang_attribute": "string",
            "charset": "string",
            "robots_meta": "string",
            "og_tags": {
                "og_title": "string",
                "og_description": "string",
                "og_image": "string",
                "og_url": "string",
                "og_type": "string"
            },
            "twitter_tags": {
                "twitter_card": "string",
                "twitter_title": "string",
                "twitter_description": "string",
                "twitter_image": "string"
            },
            "structured_data": {
                "has_schema_org": "boolean",
                "schema_types": ["string"],
                "structured_data_errors": ["string"]
            }
        },
        "seo_elements_extracted": {
            "headings": [
                {"tag": "string", "text": "string", "position": "integer"}
            ],
            "heading_structure": {
                "h1_count": "integer",
                "h2_count": "integer",
                "h3_count": "integer",
                "h4_count": "integer",
                "h5_count": "integer",
                "h6_count": "integer",
                "total_headings": "integer"
            },
            "images": [
                {
                    "src": "string",
                    "alt": "string",
                    "title": "string",
                    "has_alt": "boolean",
                    "is_decorative": "boolean",
                    "file_size_estimate": "string"
                }
            ],
            "links": [
                {
                    "href": "string",
                    "text": "string",
                    "type": "internal/external",
                    "is_follow": "boolean",
                    "has_title": "boolean",
                    "anchor_text_length": "integer"
                }
            ],
            "internal_links_count": "integer",
            "external_links_count": "integer",
            "main_text_snippet": "string",
            "word_count_total": "integer",
            "paragraph_count": "integer",
            "sentence_count": "integer",
            "average_sentence_length": "float",
            "readability_metrics": {
                "flesch_reading_ease": "float",
                "avg_words_per_sentence": "float",
                "complex_words_percentage": "float"
            }
        },
        "technical_seo_analysis": {
            "page_speed_factors": {
                "render_blocking_resources": "integer",
                "inline_styles_count": "integer",
                "inline_scripts_count": "integer",
                "external_stylesheets": "integer",
                "external_scripts": "integer"
            },
            "mobile_optimization": {
                "has_viewport_meta": "boolean",
                "viewport_content": "string",
                "responsive_design_indicators": ["string"]
            },
            "security_headers": {
                "has_https": "boolean",
                "security_issues": ["string"]
            },
            "accessibility": {
                "images_without_alt": "integer",
                "headings_structure_issues": ["string"],
                "accessibility_score": "integer"
            }
        },
        "seo_analysis_results": {
            "overall_seo_score": "integer",
            "overall_content_quality_relevance": "string",
            "keyword_analysis": {
                "primary_keywords": ["string"],
                "secondary_keywords": ["string"],
                "keyword_density": "float",
                "keyword_usage_comment": "string",
                "keyword_opportunities": ["string"]
            },
            "title_tag_analysis": {
                "score": "integer",
                "issues": ["string"],
                "recommendations": ["string"]
            },
            "meta_description_analysis": {
                "score": "integer",
                "issues": ["string"],
                "recommendations": ["string"]
            },
            "heading_structure_analysis": {
                "score": "integer",
                "structure_quality": "string",
                "issues": ["string"],
                "recommendations": ["string"]
            },
            "image_optimization_analysis": {
                "score": "integer",
                "total_images": "integer",
                "images_without_alt": "integer",
                "optimization_issues": ["string"],
                "recommendations": ["string"]
            },
            "linking_analysis": {
                "score": "integer",
                "internal_linking_quality": "string",
                "external_linking_quality": "string",
                "issues": ["string"],
                "recommendations": ["string"]
            },
            "content_analysis": {
                "score": "integer",
                "word_count_assessment": "string",
                "content_structure_quality": "string",
                "readability_assessment": "string",
                "recommendations": ["string"]
            },
            "technical_seo_analysis": {
                "score": "integer",
                "mobile_friendliness": "string",
                "page_speed_assessment": "string",
                "technical_issues": ["string"],
                "recommendations": ["string"]
            },
            "social_media_optimization": {
                "score": "integer",
                "og_tags_quality": "string",
                "twitter_tags_quality": "string",
                "issues": ["string"],
                "recommendations": ["string"]
            },
            "structured_data_analysis": {
                "score": "integer",
                "implementation_quality": "string",
                "missing_opportunities": ["string"],
                "recommendations": ["string"]
            },
            "competitive_analysis": {
                "content_uniqueness": "string",
                "competitive_advantages": ["string"],
                "improvement_opportunities": ["string"]
            },
            "actionable_recommendations": [
                {
                    "priority": "high/medium/low",
                    "category": "string",
                    "recommendation": "string",
                    "expected_impact": "string"
                }
            ],
            "next_steps": ["string"]
        }
    } 