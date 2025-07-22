#!/usr/bin/env python3
"""
Job Search Engine Module

This module provides the core functionality for intelligent job discovery
using OpenAI's web search API. It handles job searching, filtering, and
data extraction across multiple company career pages.

Features:
- AI-powered job discovery using OpenAI API
- Intelligent filtering based on configurable criteria
- Multi-company batch processing
- Structured data extraction and validation
- Professional error handling and logging
"""

import os
import sys
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

import openai

# Add project root to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.config import FILTERING_CRITERIA, FILES, OPENAI_SETTINGS, OUTPUT_SETTINGS


class JobSearchEngine:
    """
    AI-powered job search engine for discovering relevant opportunities.
    
    This class handles the complete job discovery workflow:
    - Loading company information from CSV files
    - Executing AI-powered searches using OpenAI API
    - Filtering results based on configurable criteria
    - Extracting structured job data from search results
    - Generating comprehensive reports and exports
    
    Attributes:
        api_key (str): OpenAI API key for authentication
        client (openai.OpenAI): Configured OpenAI client instance
        logger (logging.Logger): Logger for tracking operations
        companies (List[Dict]): List of companies to monitor
    """
    """
    Intelligent job search engine using OpenAI's web search API.
    
    This class provides comprehensive job discovery capabilities including:
    - Company-specific job searching
    - Intelligent filtering based on criteria
    - Structured data extraction
    - Progress tracking and logging
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the job search engine with proper configuration.
        
        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, 
                                   will be loaded from configuration
        
        Raises:
            ValueError: If OpenAI API key is not configured
            ConnectionError: If unable to validate API connection
        """
        # Configure OpenAI client
        self.api_key = api_key or OPENAI_SETTINGS.get("api_key")
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            raise ValueError(
                "OpenAI API key not configured. Please set OPENAI_API_KEY "
                "environment variable or provide api_key parameter."
            )
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Configure search settings
        self.model = OPENAI_SETTINGS.get("model", "gpt-4")
        self.max_retries = OPENAI_SETTINGS.get("max_retries", 3)
        
        # Load filtering criteria
        self.filtering_criteria = FILTERING_CRITERIA
        
        # Setup professional logging
        self._setup_logging()
        
        # Initialize results storage
        self.search_results = []
        
        self.logger.info("Job Search Engine initialized successfully")

    def _setup_logging(self) -> None:
        """Configure professional logging for the search engine."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
    def load_companies(self) -> List[Dict[str, str]]:
        """
        Load companies from CSV file.
        
        Returns:
            List of dictionaries containing company information
        """
        import pandas as pd
        
        try:
            df = pd.read_csv(self.companies_file)
            companies = df.to_dict('records')
            self.logger.info(f"Loaded {len(companies)} companies from {self.companies_file}")
            return companies
        except FileNotFoundError:
            self.logger.error(f"Companies file not found: {self.companies_file}")
            print(f"Error: {self.companies_file} not found.")
            print("Please create it with 'company_name' and 'career_page_url' columns.")
            return []
        except Exception as e:
            self.logger.error(f"Error loading companies: {e}")
            print(f"Error loading companies: {e}")
            return []
    
    def create_search_query(self, company_name: str, career_page_url: str) -> str:
        """
        Create an intelligent search query for a specific company.
        
        Args:
            company_name: Name of the company
            career_page_url: Career page URL
            
        Returns:
            Formatted search query string
        """
        # Extract key terms from filtering criteria
        locations = ', '.join(self.filtering_criteria.get('locations', []))
        keywords = ', '.join(self.filtering_criteria.get('title_keywords', []))
        experience_levels = ', '.join(self.filtering_criteria.get('experience_levels', []))
        
        query = f"""
        Find current job openings at {company_name} that match these criteria:
        
        Locations: {locations}
        Job titles containing: {keywords}
        Experience levels: {experience_levels}
        
        Search specifically on their career page: {career_page_url}
        
        Please provide:
        1. Job title
        2. Location
        3. Experience level required
        4. Brief description
        5. Application URL
        6. Department or team
        
        Focus on recent postings and include only jobs that match the location and keyword criteria.
        """
        
        return query.strip()
    
    def search_company_jobs(self, company_name: str, career_page_url: str) -> List[Dict]:
        """
        Search for jobs at a specific company using OpenAI web search.
        
        Args:
            company_name: Name of the company
            career_page_url: Career page URL
            
        Returns:
            List of job dictionaries
        """
        query = self.create_search_query(company_name, career_page_url)
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Searching jobs for {company_name} (attempt {attempt + 1})")
                print(f"  Searching for jobs at {company_name}...")
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a job search assistant. You have access to web search capabilities. 
                            Search for job openings and return structured information about each job you find.
                            Only return jobs that match the specified criteria."""
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                
                jobs_text = response.choices[0].message.content
                jobs = self.extract_structured_jobs(jobs_text, company_name)
                
                self.logger.info(f"Found {len(jobs)} jobs for {company_name}")
                return jobs
                
            except Exception as e:
                self.logger.warning(f"Search attempt {attempt + 1} failed for {company_name}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"All search attempts failed for {company_name}")
                    return []
        
        return []
    
    def extract_structured_jobs(self, jobs_text: str, company_name: str) -> List[Dict]:
        """
        Extract structured job information from the AI response.
        
        Args:
            jobs_text: Raw text response from AI
            company_name: Name of the company
            
        Returns:
            List of structured job dictionaries
        """
        jobs = []
        
        # Simple parsing approach - look for job-like patterns
        lines = jobs_text.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for job title patterns
            if any(keyword in line.lower() for keyword in ['job title:', 'position:', 'role:']):
                if current_job:
                    jobs.append(current_job)
                current_job = {'company': company_name, 'found_date': datetime.now().isoformat()}
                current_job['title'] = self.clean_job_field(line)
            
            elif any(keyword in line.lower() for keyword in ['location:', 'based in:', 'office:']):
                current_job['location'] = self.clean_job_field(line)
            
            elif any(keyword in line.lower() for keyword in ['description:', 'about:', 'summary:']):
                current_job['description'] = self.clean_job_field(line)
            
            elif any(keyword in line.lower() for keyword in ['url:', 'link:', 'apply:']):
                current_job['url'] = self.clean_job_field(line)
            
            elif any(keyword in line.lower() for keyword in ['experience:', 'level:', 'years:']):
                current_job['experience_level'] = self.clean_job_field(line)
            
            elif any(keyword in line.lower() for keyword in ['department:', 'team:', 'division:']):
                current_job['department'] = self.clean_job_field(line)
        
        # Add the last job if exists
        if current_job:
            jobs.append(current_job)
        
        # Filter jobs based on criteria
        filtered_jobs = []
        for job in jobs:
            if self.meets_filtering_criteria(job):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def clean_job_field(self, field_text: str) -> str:
        """
        Clean and format job field text.
        
        Args:
            field_text: Raw field text
            
        Returns:
            Cleaned field text
        """
        # Remove field labels
        field_text = re.sub(r'^(job title|position|role|location|based in|office|description|about|summary|url|link|apply|experience|level|years|department|team|division):\s*', '', field_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        field_text = ' '.join(field_text.split())
        
        # Remove bullet points and numbering
        field_text = re.sub(r'^\s*[-•*]\s*', '', field_text)
        field_text = re.sub(r'^\s*\d+\.\s*', '', field_text)
        
        return field_text.strip()
    
    def meets_filtering_criteria(self, job: Dict) -> bool:
        """
        Check if a job meets the filtering criteria.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if job meets criteria, False otherwise
        """
        # Check location
        if 'location' in job:
            location_match = any(
                loc.lower() in job['location'].lower() 
                for loc in self.filtering_criteria.get('locations', [])
            )
            if not location_match:
                return False
        
        # Check title keywords
        if 'title' in job:
            title_match = any(
                keyword.lower() in job['title'].lower() 
                for keyword in self.filtering_criteria.get('title_keywords', [])
            )
            if not title_match:
                return False
        
        # Check experience level
        if 'experience_level' in job:
            experience_match = any(
                level.lower() in job['experience_level'].lower() 
                for level in self.filtering_criteria.get('experience_levels', [])
            )
            if not experience_match:
                return False
        
        return True
    
    def generate_unique_id(self, job: Dict) -> str:
        """
        Generate a unique ID for a job posting.
        
        Args:
            job: Job dictionary
            
        Returns:
            Unique job ID string
        """
        import hashlib
        
        # Create a string from key job attributes
        id_string = f"{job.get('company', '')}{job.get('title', '')}{job.get('location', '')}"
        
        # Generate hash
        job_hash = hashlib.md5(id_string.encode()).hexdigest()[:8]
        
        return f"job_{job_hash}"
    
    def save_results(self, all_jobs: List[Dict]):
        """
        Save search results to markdown file.
        
        Args:
            all_jobs: List of all job dictionaries
        """
        try:
            # Ensure directory exists
            results_path = Path(self.results_file)
            results_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate markdown content
            content = self.generate_markdown_report(all_jobs)
            
            # Write to file
            with open(self.results_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Results saved to {self.results_file}")
            print(f"Results saved to {self.results_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            print(f"Error saving results: {e}")
    
    def generate_markdown_report(self, all_jobs: List[Dict]) -> str:
        """
        Generate a markdown report of all jobs found.
        
        Args:
            all_jobs: List of all job dictionaries
            
        Returns:
            Markdown formatted report string
        """
        report = []
        report.append("# Job Search Results\n")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"Total jobs found: {len(all_jobs)}\n")
        
        if not all_jobs:
            report.append("No jobs found matching the criteria.\n")
            return '\n'.join(report)
        
        # Group jobs by company
        companies = {}
        for job in all_jobs:
            company = job.get('company', 'Unknown')
            if company not in companies:
                companies[company] = []
            companies[company].append(job)
        
        # Generate report for each company
        for company, jobs in companies.items():
            report.append(f"\n## {company}\n")
            report.append(f"Found {len(jobs)} jobs\n")
            
            for i, job in enumerate(jobs, 1):
                report.append(f"\n### Job {i}: {job.get('title', 'Unknown Title')}\n")
                report.append(f"- **Location:** {job.get('location', 'Not specified')}")
                report.append(f"- **Experience Level:** {job.get('experience_level', 'Not specified')}")
                report.append(f"- **Department:** {job.get('department', 'Not specified')}")
                
                if job.get('description'):
                    report.append(f"- **Description:** {job.get('description')}")
                
                if job.get('url'):
                    report.append(f"- **Apply:** [Link]({job.get('url')})")
                
                report.append(f"- **Found:** {job.get('found_date', 'Unknown')}")
                report.append("")
        
        return '\n'.join(report)
    
    def run_search(self) -> List[Dict]:
        """
        Run the complete job search process.
        
        Returns:
            List of all jobs found
        """
        print("Starting Job Search Assistant...")
        print("Using OpenAI Web Search API for intelligent job discovery")
        
        # Load companies
        companies = self.load_companies()
        if not companies:
            return []
        
        try:
            print(f"Loaded {len(companies)} companies to monitor")
            
            all_jobs = []
            
            # Search each company
            for i, company in enumerate(companies, 1):
                print(f"Processing {company['company_name']} ({i}/{len(companies)})")
                
                jobs = self.search_company_jobs(
                    company['company_name'], 
                    company['career_page_url']
                )
                
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"  Found {len(jobs)} relevant jobs")
                else:
                    print(f"  No matching jobs found")
                
                # Small delay between companies
                time.sleep(1)
            
            # Save results
            self.save_results(all_jobs)
            
            print("Job search completed successfully!")
            return all_jobs
            
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            print(f"Error during execution: {e}")
            return []


def main():
    """Main function for command-line usage."""
    # Check API key
    api_key = OPENAI_SETTINGS.get("api_key")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: OpenAI API key not configured.")
        print("Please set your API key in one of these ways:")
        print("  1. Create a .env file with OPENAI_API_KEY=your_key")
        print("  2. Set the OPENAI_API_KEY environment variable")
        print("  3. Get your API key from: https://platform.openai.com/api-keys")
        return
    
    # Run job search
    engine = JobSearchEngine()
    jobs = engine.run_search()
    
    print(f"\nSearch completed! Found {len(jobs)} total jobs.")
    

if __name__ == "__main__":
    main()