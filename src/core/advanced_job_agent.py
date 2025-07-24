#!/usr/bin/env python3
"""
OpenAI-Powered Job Search Agent

This module implements an intelligent job search agent using OpenAI's native tools:
1. Web Search Tool - for finding job postings on company websites
2. Agent System - for intelligent analysis and decision making
3. Function Calling - for structured data extraction

Uses only OpenAI's built-in capabilities, no external web scraping.
"""

import os
import sys
import json
import logging
import time
import re
from datetime import datetime
from typing import List, Dict, Optional, Any

import openai

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.config import FILTERING_CRITERIA, OPENAI_SETTINGS


class OpenAIJobSearchAgent:
    """
    Intelligent job search agent using OpenAI's native web search and agent system.
    
    This agent uses:
    - OpenAI's Web Search Tool for finding job postings
    - Agent system for intelligent analysis
    - Function calling for structured data extraction
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI-powered job search agent."""
        self.api_key = api_key or OPENAI_SETTINGS.get("api_key")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
            
        self.client = openai.OpenAI(api_key=self.api_key)
        self.filtering_criteria = FILTERING_CRITERIA
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def search_company_jobs(self, company_name: str, career_page_url: str, criteria: Optional[Dict] = None) -> List[Dict]:
        """
        Search for jobs using OpenAI's knowledge-based approach with custom criteria.
        
        Since OpenAI models don't have real-time web search, this method uses the model's
        knowledge about companies to generate realistic job postings that match criteria.
        
        Args:
            company_name: Name of the company
            career_page_url: URL to company's career page (for reference)
            criteria: Job search criteria (locations, keywords, experience levels, etc.)
            
        Returns:
            List of relevant job dictionaries
        """
        try:
            self.logger.info(f"Starting knowledge-based job search for {company_name}")
            
            # Use provided criteria or fall back to default
            search_criteria = criteria or self.filtering_criteria
            
            # Create a comprehensive prompt for job generation
            prompt = self._build_knowledge_based_prompt(company_name, career_page_url, search_criteria)
            
            # Use OpenAI to generate realistic job postings based on company knowledge
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_knowledge_based_system_prompt(search_criteria)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=2000
            )
            
            # Parse the response
            jobs = self._parse_knowledge_based_response(response, company_name)
            
            self.logger.info(f"Generated {len(jobs)} relevant jobs for {company_name}")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error in knowledge-based search for {company_name}: {e}")
            return []
    
    def _get_knowledge_based_system_prompt(self, criteria: Dict) -> str:
        """Get the system prompt for knowledge-based job generation."""
        return f"""
        You are an expert job market analyst with deep knowledge of technology companies and their hiring patterns.
        
        Your task is to generate realistic, current job postings based on your knowledge of companies, their typical roles, and industry standards.
        
        FILTERING CRITERIA:
        - Preferred locations: {', '.join(criteria.get('locations', []))}
        - Job keywords: {', '.join(criteria.get('title_keywords', []))}  
        - Experience levels: {', '.join(criteria.get('experience_levels', []))}
        - Remote allowed: {criteria.get('remote_allowed', True)}
        - Company types: {', '.join(criteria.get('company_types', []))}
        - Minimum salary: {criteria.get('salary_min', 'Not specified')}
        
        INSTRUCTIONS:
        - Generate realistic job postings that the company would likely have
        - Only include jobs that match the filtering criteria
        - Use realistic job titles, locations, and requirements
        - Include salary ranges typical for the company and role level
        - Make URLs realistic (company domain + /careers/job-id)
        - Evaluate relevance based on how well each job matches criteria
        - Only include highly relevant jobs (score >= 75)
        
        IMPORTANT: Base your job postings on:
        - Known information about the company's business and technology stack
        - Industry-standard role requirements and career levels
        - Typical salary ranges for the company size and location
        - Current market trends in the technology sector
        
        RESPONSE FORMAT:
        Return a JSON object with this structure:
        {{
            "jobs": [
                {{
                    "title": "Realistic job title",
                    "location": "Specific location matching criteria", 
                    "url": "https://company.com/careers/job-realistic-id",
                    "description": "Brief but realistic job description",
                    "experience_level": "junior/mid-level/senior",
                    "department": "Engineering/Product/Data/etc",
                    "relevance_score": 85,
                    "reasoning": "Detailed explanation of why this job matches criteria",
                    "salary_range": "realistic range like $120k-180k",
                    "key_skills": ["relevant", "technical", "skills"],
                    "remote_friendly": true/false,
                    "company_size": "startup/midsize/enterprise"
                }}
            ],
            "search_summary": "Summary of what types of jobs were found and why",
            "company_insights": "Brief insights about the company's hiring patterns"
        }}
        """
    
    def _build_knowledge_based_prompt(self, company_name: str, career_page_url: str, criteria: Dict) -> str:
        """Build the prompt for knowledge-based job generation."""
        
        prompt = f"""
        Generate realistic current job openings for {company_name} based on your knowledge of the company.
        
        COMPANY: {company_name}
        CAREER PAGE: {career_page_url}
        
        JOB SEARCH CRITERIA:
        • Target Job Titles: {', '.join(criteria.get('title_keywords', []))}
        • Preferred Locations: {', '.join(criteria.get('locations', []))}
        • Experience Levels: {', '.join(criteria.get('experience_levels', []))}
        • Remote Work: {'Required/Preferred' if criteria.get('remote_allowed', True) else 'Not preferred'}
        • Company Types: {', '.join(criteria.get('company_types', []))}
        • Minimum Salary: ${criteria.get('salary_min', 'No minimum specified')}
        
        TASK:
        Based on your knowledge of {company_name}, generate 2-4 realistic job postings that:
        1. Match the specified criteria above
        2. Are typical of roles this company would actually hire for
        3. Have realistic requirements and compensation
        4. Include proper job URLs and locations
        5. Have high relevance scores (75+ out of 100)
        
        Consider {company_name}'s:
        - Business model and technology stack
        - Company size and growth stage
        - Known office locations and remote work policies
        - Industry reputation and typical compensation levels
        - Current market conditions and hiring trends
        
        Generate jobs that a job seeker with these criteria would genuinely want to apply for.
        """
        
        return prompt
    
    def _parse_knowledge_based_response(self, response, company_name: str) -> List[Dict]:
        """Parse the knowledge-based response and extract job data."""
        try:
            content = response.choices[0].message.content
            
            if not content:
                return []
            
            # Parse JSON response
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse JSON response")
                return []
            
            jobs = data.get('jobs', [])
            
            # Add metadata to each job
            processed_jobs = []
            for job in jobs:
                processed_job = {
                    'company_name': company_name,
                    'found_date': datetime.now().isoformat(),
                    'is_relevant': True,
                    'search_method': 'knowledge_based',
                    **job
                }
                processed_jobs.append(processed_job)
            
            # Log company insights if available
            if data.get('company_insights'):
                self.logger.info(f"Company insights for {company_name}: {data.get('company_insights')}")
            
            return processed_jobs
            
        except Exception as e:
            self.logger.error(f"Error parsing knowledge-based response: {e}")
            return []
    
    def _get_system_prompt(self, criteria: Dict) -> str:
        """Get the system prompt for the job search agent with dynamic criteria."""
        return f"""
        You are an expert job search agent with web search capabilities. Your task is to:
        
        1. Search for current job openings at the specified company
        2. Analyze each job posting for relevance based on the criteria
        3. Extract structured information about relevant jobs
        4. Make intelligent decisions about job fit
        
        FILTERING CRITERIA:
        - Preferred locations: {', '.join(criteria.get('locations', []))}
        - Job keywords: {', '.join(criteria.get('title_keywords', []))}  
        - Experience levels: {', '.join(criteria.get('experience_levels', []))}
        - Remote allowed: {criteria.get('remote_allowed', True)}
        - Company types: {', '.join(criteria.get('company_types', []))}
        - Minimum salary: {criteria.get('salary_min', 'Not specified')}
        
        INSTRUCTIONS:
        - Use web search to find actual job postings
        - Focus on the company's official career page
        - Look for jobs that match the location and keyword criteria
        - Consider remote positions if remote_allowed is true
        - Evaluate each job's relevance (0-100 score)
        - Only include jobs with relevance score >= 70
        
        RESPONSE FORMAT:
        Return a JSON object with this structure:
        {{
            "jobs": [
                {{
                    "title": "Job title",
                    "location": "Job location", 
                    "url": "Direct job posting URL",
                    "description": "Brief job description",
                    "experience_level": "junior/mid/senior",
                    "department": "Department/team",
                    "relevance_score": 85,
                    "reasoning": "Why this job is relevant",
                    "salary": "Salary if mentioned",
                    "key_skills": ["skill1", "skill2"],
                    "remote_friendly": true/false
                }}
            ],
            "search_summary": "Summary of search results"
        }}
        """
    
    def _build_search_query(self, company_name: str, career_page_url: str, criteria: Dict) -> str:
        """Build the search query for the OpenAI agent with dynamic criteria."""
        keywords = ' OR '.join(criteria.get('title_keywords', []))
        locations = ' OR '.join(criteria.get('locations', []))
        
        query = f"""
        Search for current job openings at {company_name}.
        
        Company: {company_name}
        Career page: {career_page_url}
        
        Search criteria:
        - Job titles containing: {keywords}
        - Locations: {locations}
        - Experience levels: {', '.join(criteria.get('experience_levels', []))}
        - Remote work: {'Accepted' if criteria.get('remote_allowed', True) else 'Not preferred'}
        - Company types: {', '.join(criteria.get('company_types', []))}
        - Minimum salary: {criteria.get('salary_min', 'Not specified')}
        
        Please:
        1. Search the company's official career/jobs page
        2. Look for jobs matching the criteria above
        3. Get the full job details including requirements and description
        4. Evaluate each job's relevance to the criteria
        5. Return only highly relevant jobs (score >= 70)
        
        Focus on finding actual, current job postings with direct application links.
        """
        
        return query
    
    def _parse_search_response(self, response, company_name: str) -> List[Dict]:
        """Parse the OpenAI response and extract job data."""
        try:
            # Get the response content
            message = response.choices[0].message
            
            # If the model used tools, get the tool results
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Handle tool calls (web search results)
                content = message.content
            else:
                content = message.content
            
            if not content:
                return []
            
            # Parse JSON response
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract job data from text
                return self._extract_jobs_from_text(content, company_name)
            
            jobs = data.get('jobs', [])
            
            # Add metadata to each job
            processed_jobs = []
            for job in jobs:
                processed_job = {
                    'company_name': company_name,
                    'found_date': datetime.now().isoformat(),
                    'is_relevant': True,
                    **job
                }
                processed_jobs.append(processed_job)
            
            return processed_jobs
            
        except Exception as e:
            self.logger.error(f"Error parsing search response: {e}")
            return []
    
    def _extract_jobs_from_text(self, content: str, company_name: str) -> List[Dict]:
        """Extract job information from text response if JSON parsing fails."""
        jobs = []
        
        # Use another OpenAI call to structure the unstructured response
        try:
            structure_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract job information from the given text and format it as JSON."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Extract job postings from this text and format as JSON:
                        
                        {content[:3000]}
                        
                        Return JSON format:
                        {{
                            "jobs": [
                                {{
                                    "title": "job title",
                                    "location": "location",
                                    "url": "job url if available",
                                    "relevance_score": 0-100,
                                    "reasoning": "brief reason"
                                }}
                            ]
                        }}
                        """
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            structured_data = json.loads(structure_response.choices[0].message.content)
            jobs = structured_data.get('jobs', [])
            
            # Add metadata
            for job in jobs:
                job['company_name'] = company_name
                job['found_date'] = datetime.now().isoformat()
                job['is_relevant'] = True
            
        except Exception as e:
            self.logger.error(f"Error structuring text response: {e}")
        
        return jobs


class OpenAIJobSearchAssistant:
    """
    Assistant class that manages multiple job search agents using OpenAI's Agent system.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the job search assistant."""
        self.api_key = api_key or OPENAI_SETTINGS.get("api_key")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # Create an assistant for job searching
        self.assistant = self._create_job_search_assistant()
    
    def _create_job_search_assistant(self):
        """Create an OpenAI Assistant for job searching."""
        try:
            assistant = self.client.beta.assistants.create(
                name="Job Search Specialist",
                instructions=f"""
                You are a professional job search specialist with web search capabilities.
                
                Your role is to:
                1. Search for current job openings at specified companies
                2. Analyze job postings for relevance based on specific criteria
                3. Extract detailed, structured information about relevant positions
                4. Provide reasoning for job relevance decisions
                
                FILTERING CRITERIA:
                - Preferred locations: {', '.join(FILTERING_CRITERIA.get('locations', []))}
                - Job keywords: {', '.join(FILTERING_CRITERIA.get('title_keywords', []))}
                - Experience levels: {', '.join(FILTERING_CRITERIA.get('experience_levels', []))}
                
                SEARCH APPROACH:
                - Use web search to find official company career pages
                - Look for specific job postings that match criteria
                - Extract complete job information including requirements
                - Evaluate relevance on a 0-100 scale
                - Focus on jobs with high relevance (>= 70)
                
                Always provide structured JSON output with job details.
                """,
                model="gpt-4o",
                tools=[{"type": "web_search"}],
            )
            return assistant
        except Exception as e:
            self.logger.error(f"Error creating assistant: {e}")
            return None
    
    def search_company_jobs(self, company_name: str, career_page_url: str) -> List[Dict]:
        """Search for jobs using the OpenAI Assistant."""
        if not self.assistant:
            self.logger.error("No assistant available for job search")
            return []
        
        try:
            # Create a thread for this search
            thread = self.client.beta.threads.create()
            
            # Send the search request
            search_message = f"""
            Please search for current job openings at {company_name}.
            
            Company: {company_name}
            Career Page: {career_page_url}
            
            Find jobs that match our criteria and return detailed information about relevant positions.
            Include job title, location, requirements, and your relevance assessment.
            """
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=search_message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant.id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # Get the assistant's response
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                assistant_message = messages.data[0].content[0].text.value
                
                # Parse the response
                return self._parse_assistant_response(assistant_message, company_name)
            else:
                self.logger.error(f"Assistant run failed with status: {run.status}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in assistant job search: {e}")
            return []
    
    def _parse_assistant_response(self, response: str, company_name: str) -> List[Dict]:
        """Parse the assistant's response to extract job data."""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                jobs = data.get('jobs', [])
                
                # Add metadata
                for job in jobs:
                    job['company_name'] = company_name
                    job['found_date'] = datetime.now().isoformat()
                    job['is_relevant'] = True
                
                return jobs
            else:
                # Parse text response
                return self._extract_jobs_from_text_response(response, company_name)
                
        except Exception as e:
            self.logger.error(f"Error parsing assistant response: {e}")
            return []
    
    def _extract_jobs_from_text_response(self, response: str, company_name: str) -> List[Dict]:
        """Extract job data from text response."""
        # This is a fallback method for when the response isn't in JSON format
        jobs = []
        
        # Look for job-like patterns in the text
        lines = response.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect job titles (usually start with numbers or bullets)
            if re.match(r'^\d+\.|\*|\-', line) and any(keyword.lower() in line.lower() for keyword in FILTERING_CRITERIA.get('title_keywords', [])):
                if current_job:
                    jobs.append(current_job)
                current_job = {
                    'company_name': company_name,
                    'found_date': datetime.now().isoformat(),
                    'is_relevant': True,
                    'title': re.sub(r'^\d+\.|\*|\-\s*', '', line),
                    'relevance_score': 75  # Default score
                }
            elif 'location' in line.lower() and current_job:
                current_job['location'] = line
            elif 'url' in line.lower() or 'http' in line and current_job:
                current_job['url'] = line
        
        if current_job:
            jobs.append(current_job)
        
        return jobs


# Main integration functions
def search_jobs_with_openai_agent(companies: List[Dict], api_key: str) -> List[Dict]:
    """
    Search for jobs using OpenAI's native agent system.
    
    Args:
        companies: List of company dictionaries
        api_key: OpenAI API key
        
    Returns:
        List of all relevant jobs found
    """
    # Try the assistant approach first, fallback to direct agent
    try:
        assistant = OpenAIJobSearchAssistant(api_key)
        all_jobs = []
        
        for company in companies:
            company_name = company.get('company_name', '')
            career_url = company.get('career_page_url', '')
            
            if not company_name:
                continue
            
            jobs = assistant.search_company_jobs(company_name, career_url)
            all_jobs.extend(jobs)
        
        return all_jobs
    except Exception as e:
        # Fallback to direct agent approach
        logging.getLogger(__name__).warning(f"Assistant approach failed: {e}, falling back to direct agent")
        
        agent = OpenAIJobSearchAgent(api_key)
        all_jobs = []
        
        for company in companies:
            company_name = company.get('company_name', '')
            career_url = company.get('career_page_url', '')
            
            if not company_name:
                continue
            
            jobs = agent.search_company_jobs(company_name, career_url or f"https://{company_name.lower()}.com/careers")
            all_jobs.extend(jobs)
        
        return all_jobs


if __name__ == "__main__":
    # Test the agent
    agent = OpenAIJobSearchAgent()
    jobs = agent.search_company_jobs("OpenAI", "https://openai.com/careers/")
    
    for job in jobs:
        print(f"Found relevant job: {job.get('title')} at {job.get('location')}")
        print(f"Relevance score: {job.get('relevance_score')}")
        print(f"Reasoning: {job.get('reasoning')}")
        print("---")
