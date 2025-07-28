#!/usr/bin/env python3
"""
Enhanced Job Search Engine with Real Web Search Capabilities

This module orchestrates job discovery using real web search APIs
and OpenAI-powered structured data extraction.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path

from .web_search_engine import WebSearchEngine, JobSearchOrchestrator, JobListing
from .advanced_job_agent import OpenAIJobSearchAgent  # Keep for backup
from config.config import FILTERING_CRITERIA, FILES, OPENAI_SETTINGS

logger = logging.getLogger(__name__)


class EnhancedJobSearchEngine:
    """
    Enhanced Job Search Engine with real web search capabilities.
    
    This engine combines:
    - Real web search through Google/Bing/DuckDuckGo APIs
    - OpenAI-powered structured data extraction
    - Company-specific job discovery
    - Intelligent filtering and deduplication
    """
    
    def __init__(self, openai_api_key: str, google_api_key: Optional[str] = None,
                 bing_api_key: Optional[str] = None, custom_search_engine_id: Optional[str] = None):
        """
        Initialize the job search engine with API keys.
        
        Args:
            openai_api_key: OpenAI API key for data extraction
            google_api_key: Google Custom Search API key (optional)
            bing_api_key: Bing Search API key (optional)  
            custom_search_engine_id: Google Custom Search Engine ID (optional)
        """
        self.openai_api_key = openai_api_key
        
        # Initialize enhanced web search engine
        self.web_search_engine = WebSearchEngine(
            openai_api_key=openai_api_key,
            google_api_key=google_api_key,
            bing_api_key=bing_api_key,
            custom_search_engine_id=custom_search_engine_id
        )
        
        # Keep backup agent for compatibility
        self.backup_agent = OpenAIJobSearchAgent(openai_api_key)
        
        # Load filtering criteria
        self.filtering_criteria = FILTERING_CRITERIA
        
        logger.info("Enhanced JobSearchEngine initialized with real web search capabilities")

    def search_company_jobs(self, company_name: str, career_page_url: str = "", 
                          location: str = "") -> str:
        """
        Search for jobs from a specific company using real web search.
        
        Args:
            company_name: Name of the company
            career_page_url: Company career page URL (used for context)
            location: Optional location filter
            
        Returns:
            Raw search results as string (for compatibility)
        """
        logger.info(f"Searching jobs for {company_name} with enhanced web search")
        
        try:
            # Use enhanced web search
            search_results = self.web_search_engine.search_company_jobs(
                company_name=company_name,
                location=location,
                max_results=20
            )
            
            if not search_results:
                logger.warning(f"No web search results found for {company_name}, trying backup agent")
                # Fallback to backup agent
                return self.backup_agent.search_company_jobs(company_name, career_page_url)
            
            # Format results for compatibility with existing code
            formatted_results = []
            for result in search_results:
                formatted_result = f"""
Title: {result.title}
URL: {result.url}
Description: {result.snippet}
Source: {result.source}
---
"""
                formatted_results.append(formatted_result)
            
            results_text = "\n".join(formatted_results)
            logger.info(f"Found {len(search_results)} web search results for {company_name}")
            
            return results_text
            
        except Exception as e:
            logger.error(f"Error in enhanced search for {company_name}: {e}")
            # Fallback to backup agent
            logger.info(f"Falling back to backup agent for {company_name}")
            return self.backup_agent.search_company_jobs(company_name, career_page_url)

    def extract_structured_jobs(self, search_results: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Extract structured job data from search results.
        
        Args:
            search_results: Raw search results string
            company_name: Company name for context
            
        Returns:
            List of structured job dictionaries
        """
        logger.info(f"Extracting structured jobs for {company_name}")
        
        try:
            # If we have web search results, parse them back to SearchResult objects
            if "Source:" in search_results and "URL:" in search_results:
                # Parse web search results
                search_result_objects = self._parse_search_results_string(search_results)
                
                # Extract using web search engine
                job_listings = self.web_search_engine.extract_job_listings(
                    search_result_objects, company_name
                )
                
                # Convert to dictionaries for compatibility
                structured_jobs = []
                for job in job_listings:
                    job_dict = {
                        'job_id': job.job_id,
                        'company_name': job.company_name,
                        'job_title': job.job_title,
                        'location': job.location or '',
                        'url': job.url or '',
                        'description': job.description or '',
                        'employment_type': job.employment_type or '',
                        'experience_level': job.experience_level or '',
                        'salary_range': job.salary_range or '',
                        'posted_date': job.posted_date or '',
                        'source': job.source or 'web_search'
                    }
                    structured_jobs.append(job_dict)
                
                # Apply filtering
                filtered_jobs = self._apply_filtering(structured_jobs)
                
                logger.info(f"Extracted {len(filtered_jobs)} filtered jobs for {company_name}")
                return filtered_jobs
            
            else:
                # Fallback to backup agent for non-web search results
                logger.info(f"Using backup agent extraction for {company_name}")
                return self.backup_agent.extract_structured_jobs(search_results, company_name)
                
        except Exception as e:
            logger.error(f"Error extracting structured jobs for {company_name}: {e}")
            # Final fallback
            return self.backup_agent.extract_structured_jobs(search_results, company_name)

    def _parse_search_results_string(self, results_string: str) -> List:
        """Parse search results string back to SearchResult objects."""
        from .web_search_engine import SearchResult
        
        results = []
        sections = results_string.split('---')
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            title = url = snippet = source = ""
            
            for line in lines:
                if line.startswith('Title:'):
                    title = line.replace('Title:', '').strip()
                elif line.startswith('URL:'):
                    url = line.replace('URL:', '').strip()
                elif line.startswith('Description:'):
                    snippet = line.replace('Description:', '').strip()
                elif line.startswith('Source:'):
                    source = line.replace('Source:', '').strip()
            
            if title and url:
                results.append(SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source=source
                ))
        
        return results

    def _apply_filtering(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filtering criteria to job listings."""
        if not jobs:
            return jobs
        
        filtered_jobs = []
        
        for job in jobs:
            # Check if job meets filtering criteria
            if self._meets_criteria(job):
                filtered_jobs.append(job)
        
        logger.info(f"Filtered {len(jobs)} jobs down to {len(filtered_jobs)} matching criteria")
        return filtered_jobs

    def _meets_criteria(self, job: Dict[str, Any]) -> bool:
        """Check if a job meets the filtering criteria."""
        try:
            job_text = (
                f"{job.get('job_title', '')} {job.get('description', '')} "
                f"{job.get('location', '')} {job.get('experience_level', '')}"
            ).lower()
            
            # Check location criteria
            locations = self.filtering_criteria.get('locations', [])
            if locations:
                location_match = any(
                    location.lower() in job_text 
                    for location in locations
                )
                if not location_match:
                    return False
            
            # Check title keywords
            title_keywords = self.filtering_criteria.get('title_keywords', [])
            if title_keywords:
                title_match = any(
                    keyword.lower() in job_text 
                    for keyword in title_keywords
                )
                if not title_match:
                    return False
            
            # Check experience levels
            experience_levels = self.filtering_criteria.get('experience_levels', [])
            if experience_levels:
                experience_match = any(
                    level.lower() in job_text 
                    for level in experience_levels
                )
                # If no experience level mentioned, assume it's okay
                if job.get('experience_level') and not experience_match:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking criteria for job {job.get('job_id', 'unknown')}: {e}")
            return True  # Include job if filtering fails

    def run_batch_search(self, companies_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Run batch job search across multiple companies using enhanced web search.
        
        Args:
            companies_data: List of company information dictionaries
            
        Returns:
            Comprehensive search results
        """
        logger.info(f"Starting enhanced batch search for {len(companies_data)} companies")
        
        try:
            # Create orchestrator with enhanced search
            orchestrator = JobSearchOrchestrator(
                web_search_engine=self.web_search_engine
            )
            
            # Run comprehensive search
            results = orchestrator.run_comprehensive_search(companies_data)
            
            logger.info(f"Enhanced batch search completed: {results.get('total_jobs_found', 0)} jobs found")
            return results
            
        except Exception as e:
            logger.error(f"Error in enhanced batch search: {e}")
            # Fallback to individual searches
            return self._fallback_batch_search(companies_data)

    def _fallback_batch_search(self, companies_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fallback batch search using individual company searches."""
        logger.info("Using fallback batch search method")
        
        results = {
            'success': True,
            'total_companies_searched': len(companies_data),
            'total_jobs_found': 0,
            'company_results': [],
            'search_timestamp': datetime.now().isoformat(),
            'fallback_mode': True
        }
        
        for company_info in companies_data:
            try:
                company_name = company_info.get('company_name', '')
                career_url = company_info.get('career_page_url', '')
                
                if not company_name:
                    continue
                
                # Search for jobs
                search_results = self.search_company_jobs(company_name, career_url)
                job_listings = self.extract_structured_jobs(search_results, company_name)
                
                results['total_jobs_found'] += len(job_listings)
                results['company_results'].append({
                    'company_name': company_name,
                    'jobs_found': len(job_listings),
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"Error in fallback search for {company_name}: {e}")
                results['company_results'].append({
                    'company_name': company_name,
                    'jobs_found': 0,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results

    def discover_jobs_for_companies(self, csv_file_path: str = None) -> Dict[str, Any]:
        """
        Discover jobs for companies listed in CSV file.
        
        Args:
            csv_file_path: Path to companies CSV file
            
        Returns:
            Discovery results summary
        """
        if not csv_file_path:
            csv_file_path = FILES.get("companies_csv", "config/companies_to_watch.csv")
        
        logger.info(f"Discovering jobs from companies in {csv_file_path}")
        
        try:
            # Load companies from CSV
            companies_df = pd.read_csv(csv_file_path)
            
            # Convert to list of dictionaries
            companies_data = []
            for _, row in companies_df.iterrows():
                company_data = {
                    'company_name': row.get('company_name', ''),
                    'career_page_url': row.get('career_page_url', ''),
                    'location': row.get('location', '')
                }
                if company_data['company_name']:
                    companies_data.append(company_data)
            
            logger.info(f"Loaded {len(companies_data)} companies from CSV")
            
            # Run batch search
            return self.run_batch_search(companies_data)
            
        except Exception as e:
            logger.error(f"Error discovering jobs from CSV: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_companies_searched': 0,
                'total_jobs_found': 0
            }

    def get_search_capabilities(self) -> Dict[str, Any]:
        """Get information about search capabilities."""
        return {
            'enhanced_search': True,
            'web_search_engine': self.web_search_engine.get_search_statistics(),
            'backup_agent_available': bool(self.backup_agent),
            'filtering_criteria': self.filtering_criteria
        }


# Maintain backward compatibility with original JobSearchEngine
JobSearchEngine = EnhancedJobSearchEngine
