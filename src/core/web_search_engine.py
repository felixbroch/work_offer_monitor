#!/usr/bin/env python3
"""
Enhanced Web Search Engine for Job Search Assistant

This module provides real web search capabilities using multiple search providers
with OpenAI-powered structured data extraction for job listings.
"""

import json
import logging
import time
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import re
from urllib.parse import quote_plus, urljoin
from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class JobListing:
    """Structured job listing data."""
    job_id: str
    company_name: str
    job_title: str
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    employment_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    experience_level: Optional[str] = None  # Entry, Mid, Senior, etc.
    salary_range: Optional[str] = None
    posted_date: Optional[str] = None
    source: Optional[str] = None  # Search provider used


@dataclass
class SearchResult:
    """Web search result data."""
    title: str
    url: str
    snippet: str
    source: str


class WebSearchEngine:
    """
    Enhanced web search engine with multiple providers and OpenAI integration.
    
    Supports:
    - Google Search API (Custom Search Engine)
    - Bing Search API
    - DuckDuckGo (free fallback)
    - Direct job site scraping
    """
    
    def __init__(self, openai_api_key: str, google_api_key: Optional[str] = None, 
                 bing_api_key: Optional[str] = None, custom_search_engine_id: Optional[str] = None):
        """
        Initialize the web search engine.
        
        Args:
            openai_api_key: OpenAI API key for structured data extraction
            google_api_key: Google Custom Search API key (optional)
            bing_api_key: Bing Search API key (optional)
            custom_search_engine_id: Google Custom Search Engine ID (optional)
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.google_api_key = google_api_key
        self.bing_api_key = bing_api_key
        self.custom_search_engine_id = custom_search_engine_id
        
        # Job sites to prioritize in searches
        self.job_sites = [
            "linkedin.com/jobs", "indeed.com", "glassdoor.com", 
            "monster.com", "ziprecruiter.com", "simplyhired.com",
            "careerbuilder.com", "dice.com", "stackoverflow.com/jobs"
        ]
        
        # Request session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_company_jobs(self, company_name: str, location: str = "", 
                          max_results: int = 20) -> List[SearchResult]:
        """
        Search for job listings from a specific company using multiple search providers.
        
        Args:
            company_name: Name of the company to search for
            location: Optional location filter
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        logger.info(f"Starting job search for {company_name}")
        
        # Build search queries
        queries = self._build_search_queries(company_name, location)
        all_results = []
        
        for query in queries:
            try:
                # Try Google Search first
                if self.google_api_key and self.custom_search_engine_id:
                    results = self._google_search(query, max_results // len(queries))
                    all_results.extend(results)
                
                # Try Bing Search as backup
                elif self.bing_api_key:
                    results = self._bing_search(query, max_results // len(queries))
                    all_results.extend(results)
                
                # Fallback to DuckDuckGo
                else:
                    results = self._duckduckgo_search(query, max_results // len(queries))
                    all_results.extend(results)
                    
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error searching with query '{query}': {e}")
                continue
        
        # Remove duplicates and filter results
        unique_results = self._deduplicate_results(all_results)
        filtered_results = self._filter_job_results(unique_results, company_name)
        
        logger.info(f"Found {len(filtered_results)} unique job results for {company_name}")
        return filtered_results[:max_results]

    def _build_search_queries(self, company_name: str, location: str = "") -> List[str]:
        """Build optimized search queries for job listings."""
        base_queries = [
            f'"{company_name}" jobs careers',
            f'"{company_name}" hiring opportunities',
            f'site:linkedin.com/jobs "{company_name}"',
            f'"{company_name}" job openings'
        ]
        
        if location:
            location_queries = [
                f'"{company_name}" jobs {location}',
                f'"{company_name}" careers {location}'
            ]
            base_queries.extend(location_queries)
        
        return base_queries

    def _google_search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.custom_search_engine_id,
                'q': query,
                'num': min(max_results, 10)  # Google allows max 10 per request
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    source='google'
                )
                results.append(result)
            
            logger.info(f"Google search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []

    def _bing_search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Bing Search API."""
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': self.bing_api_key}
            params = {
                'q': query,
                'count': min(max_results, 50),
                'mkt': 'en-US'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('webPages', {}).get('value', []):
                result = SearchResult(
                    title=item.get('name', ''),
                    url=item.get('url', ''),
                    snippet=item.get('snippet', ''),
                    source='bing'
                )
                results.append(result)
            
            logger.info(f"Bing search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []

    def _duckduckgo_search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using DuckDuckGo (free fallback)."""
        try:
            # DuckDuckGo Instant Answer API (limited but free)
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Process related topics (limited results)
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and 'FirstURL' in topic:
                    result = SearchResult(
                        title=topic.get('Text', '').split(' - ')[0],
                        url=topic.get('FirstURL', ''),
                        snippet=topic.get('Text', ''),
                        source='duckduckgo'
                    )
                    results.append(result)
            
            logger.info(f"DuckDuckGo search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate search results based on URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results

    def _filter_job_results(self, results: List[SearchResult], company_name: str) -> List[SearchResult]:
        """Filter results to focus on job-related content."""
        job_keywords = [
            'job', 'career', 'position', 'opening', 'hiring', 'employment', 
            'vacancy', 'opportunity', 'role', 'work', 'join our team'
        ]
        
        filtered_results = []
        
        for result in results:
            # Check if result contains job-related keywords
            text_to_check = (result.title + " " + result.snippet).lower()
            
            # Must contain company name
            if company_name.lower() not in text_to_check:
                continue
            
            # Must contain job-related keywords
            if any(keyword in text_to_check for keyword in job_keywords):
                filtered_results.append(result)
            
            # Prioritize known job sites
            elif any(site in result.url.lower() for site in self.job_sites):
                filtered_results.append(result)
        
        return filtered_results

    def extract_job_listings(self, search_results: List[SearchResult], 
                           company_name: str) -> List[JobListing]:
        """
        Extract structured job listings from search results using OpenAI.
        
        Args:
            search_results: List of search results to process
            company_name: Company name for context
            
        Returns:
            List of structured JobListing objects
        """
        logger.info(f"Extracting job listings from {len(search_results)} search results")
        
        if not search_results:
            return []
        
        try:
            # Prepare search results for OpenAI
            results_text = self._format_results_for_extraction(search_results)
            
            # Use OpenAI function calling for structured extraction
            job_listings = self._extract_with_openai(results_text, company_name)
            
            logger.info(f"Extracted {len(job_listings)} structured job listings")
            return job_listings
            
        except Exception as e:
            logger.error(f"Error extracting job listings: {e}")
            return []

    def _format_results_for_extraction(self, search_results: List[SearchResult]) -> str:
        """Format search results for OpenAI processing."""
        formatted_results = []
        
        for i, result in enumerate(search_results, 1):
            formatted_result = f"""
Result {i}:
Title: {result.title}
URL: {result.url}
Snippet: {result.snippet}
Source: {result.source}
---
"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)

    def _extract_with_openai(self, results_text: str, company_name: str) -> List[JobListing]:
        """Extract structured job data using OpenAI function calling."""
        
        # Define the function schema for job extraction
        function_schema = {
            "name": "extract_job_listings",
            "description": "Extract structured job listing information from search results",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_listings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "job_title": {"type": "string", "description": "Job title or position name"},
                                "company_name": {"type": "string", "description": "Company name"},
                                "location": {"type": "string", "description": "Job location"},
                                "url": {"type": "string", "description": "Job posting URL"},
                                "employment_type": {"type": "string", "description": "Employment type (Full-time, Part-time, Contract, etc.)"},
                                "experience_level": {"type": "string", "description": "Experience level (Entry, Mid, Senior, etc.)"},
                                "description": {"type": "string", "description": "Job description or summary"},
                                "salary_range": {"type": "string", "description": "Salary range if mentioned"},
                                "posted_date": {"type": "string", "description": "Date posted if available"}
                            },
                            "required": ["job_title", "company_name"]
                        }
                    }
                },
                "required": ["job_listings"]
            }
        }
        
        system_prompt = f"""
You are a job search specialist. Extract structured job listing information from the provided search results.
Focus on jobs from {company_name} or jobs that mention this company.

Guidelines:
1. Only extract genuine job listings, not general company information
2. Ensure job_title is descriptive and specific
3. Include location when available
4. Extract employment type and experience level when mentioned
5. Keep descriptions concise but informative
6. If salary is mentioned, include the range
7. Generate a unique job_id based on company + title + location

Be thorough but accurate - only include jobs that are clearly job postings.
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract job listings from these search results:\n\n{results_text}"}
                ],
                functions=[function_schema],
                function_call={"name": "extract_job_listings"},
                temperature=0.1
            )
            
            # Parse the function call response
            function_call = response.choices[0].message.function_call
            if function_call and function_call.name == "extract_job_listings":
                extracted_data = json.loads(function_call.arguments)
                job_listings = []
                
                for job_data in extracted_data.get("job_listings", []):
                    # Generate unique job ID
                    job_id = self._generate_job_id(
                        job_data.get("company_name", company_name),
                        job_data.get("job_title", ""),
                        job_data.get("location", "")
                    )
                    
                    job_listing = JobListing(
                        job_id=job_id,
                        company_name=job_data.get("company_name", company_name),
                        job_title=job_data.get("job_title", ""),
                        location=job_data.get("location"),
                        url=job_data.get("url"),
                        description=job_data.get("description"),
                        employment_type=job_data.get("employment_type"),
                        experience_level=job_data.get("experience_level"),
                        salary_range=job_data.get("salary_range"),
                        posted_date=job_data.get("posted_date"),
                        source="web_search"
                    )
                    job_listings.append(job_listing)
                
                return job_listings
            
            logger.warning("No function call response from OpenAI")
            return []
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            return []

    def _generate_job_id(self, company: str, title: str, location: str = "") -> str:
        """Generate a unique job ID."""
        # Clean and combine components
        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company.lower())
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
        clean_location = re.sub(r'[^a-zA-Z0-9]', '', location.lower()) if location else ""
        
        # Create hash-like ID
        combined = f"{clean_company}_{clean_title}_{clean_location}"
        return combined[:50]  # Limit length

    def search_multiple_companies(self, companies: List[Dict[str, str]], 
                                max_results_per_company: int = 10) -> Dict[str, List[JobListing]]:
        """
        Search for jobs from multiple companies.
        
        Args:
            companies: List of company dictionaries with 'name' and optional 'location'
            max_results_per_company: Maximum results per company
            
        Returns:
            Dictionary mapping company names to their job listings
        """
        all_company_jobs = {}
        
        for company_info in companies:
            company_name = company_info.get('company_name') or company_info.get('name', '')
            location = company_info.get('location', '')
            
            if not company_name:
                logger.warning(f"Skipping company with missing name: {company_info}")
                continue
            
            try:
                logger.info(f"Searching jobs for {company_name}")
                
                # Search for jobs
                search_results = self.search_company_jobs(
                    company_name=company_name,
                    location=location,
                    max_results=max_results_per_company * 2  # Get extra for filtering
                )
                
                # Extract structured job listings
                job_listings = self.extract_job_listings(search_results, company_name)
                
                all_company_jobs[company_name] = job_listings
                logger.info(f"Found {len(job_listings)} jobs for {company_name}")
                
                # Rate limiting between companies
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {company_name}: {e}")
                all_company_jobs[company_name] = []
        
        return all_company_jobs

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about search capabilities."""
        return {
            "providers_available": {
                "google": bool(self.google_api_key and self.custom_search_engine_id),
                "bing": bool(self.bing_api_key),
                "duckduckgo": True  # Always available as fallback
            },
            "job_sites_monitored": len(self.job_sites),
            "openai_enabled": bool(self.openai_client)
        }


class JobSearchOrchestrator:
    """
    High-level orchestrator for job searches across multiple companies.
    Integrates with database and provides comprehensive search workflows.
    """
    
    def __init__(self, web_search_engine: WebSearchEngine, database=None, history_tracker=None):
        """
        Initialize the job search orchestrator.
        
        Args:
            web_search_engine: WebSearchEngine instance
            database: Database connection (optional)
            history_tracker: History tracker instance (optional)
        """
        self.search_engine = web_search_engine
        self.database = database
        self.history_tracker = history_tracker
        self.logger = logging.getLogger(__name__)

    def run_comprehensive_search(self, companies: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Run a comprehensive job search across multiple companies.
        
        Args:
            companies: List of company information dictionaries
            
        Returns:
            Comprehensive search results with statistics
        """
        start_time = datetime.now()
        self.logger.info(f"Starting comprehensive search for {len(companies)} companies")
        
        # Search all companies
        all_results = self.search_engine.search_multiple_companies(companies)
        
        # Process results
        total_jobs = 0
        company_summaries = []
        
        for company_name, job_listings in all_results.items():
            total_jobs += len(job_listings)
            
            # Process through history tracker if available
            if self.history_tracker:
                try:
                    summary = self.history_tracker.process_company_jobs(company_name, [
                        {
                            'job_id': job.job_id,
                            'company_name': job.company_name,
                            'job_title': job.job_title,
                            'location': job.location,
                            'url': job.url,
                            'description': job.description
                        }
                        for job in job_listings
                    ])
                    company_summaries.append({
                        'company_name': company_name,
                        'jobs_found': len(job_listings),
                        'summary': summary
                    })
                except Exception as e:
                    self.logger.error(f"Error processing history for {company_name}: {e}")
                    company_summaries.append({
                        'company_name': company_name,
                        'jobs_found': len(job_listings),
                        'error': str(e)
                    })
            else:
                company_summaries.append({
                    'company_name': company_name,
                    'jobs_found': len(job_listings)
                })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'success': True,
            'total_companies_searched': len(companies),
            'total_jobs_found': total_jobs,
            'search_duration_seconds': duration,
            'company_results': company_summaries,
            'search_timestamp': start_time.isoformat(),
            'search_engine_stats': self.search_engine.get_search_statistics()
        }
