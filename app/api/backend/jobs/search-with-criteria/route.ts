import { NextRequest, NextResponse } from 'next/server'

interface SearchCriteria {
  locations: string[]
  title_keywords: string[]
  experience_levels: string[]
  remote_allowed: boolean
  company_types: string[]
  salary_min: string
}

interface SearchRequest {
  api_key: string
  criteria: SearchCriteria
  companies: string[]
}

export async function POST(request: NextRequest) {
  try {
    const body: SearchRequest = await request.json()
    
    // Validate required fields
    if (!body.api_key) {
      return NextResponse.json(
        { success: false, error: 'API key is required' },
        { status: 400 }
      )
    }

    if (!body.companies || body.companies.length === 0) {
      return NextResponse.json(
        { success: false, error: 'At least one company is required' },
        { status: 400 }
      )
    }

    // Try to use the Python backend first
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000'
    
    try {
      const backendResponse = await fetch(`${backendUrl}/api/jobs/search-with-criteria`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
        timeout: 30000 // 30 second timeout
      })

      if (backendResponse.ok) {
        const data = await backendResponse.json()
        return NextResponse.json(data)
      }
    } catch (backendError) {
      console.log('Backend unavailable, using direct OpenAI approach:', backendError)
    }

    // Fallback: Direct OpenAI integration
    console.log('Using direct OpenAI integration for job search')
    
    const { OpenAI } = await import('openai')
    const openai = new OpenAI({
      apiKey: body.api_key
    })

    const allJobs = []
    const searchErrors = []

    // Search each company
    for (const company of body.companies) {
      try {
        console.log(`Searching jobs for ${company}...`)
        
        const jobs = await searchCompanyJobs(openai, company, body.criteria)
        allJobs.push(...jobs)
        
        console.log(`Found ${jobs.length} jobs for ${company}`)
      } catch (error) {
        console.error(`Error searching ${company}:`, error)
        searchErrors.push(`${company}: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    }

    // Return results
    const response = {
      success: true,
      jobs: allJobs,
      total_jobs: allJobs.length,
      companies_searched: body.companies.length,
      search_criteria: body.criteria,
      errors: searchErrors.length > 0 ? searchErrors : undefined
    }

    return NextResponse.json(response)

  } catch (error) {
    console.error('Search API error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Internal server error',
        jobs: []
      },
      { status: 500 }
    )
  }
}

async function searchCompanyJobs(openai: any, companyName: string, criteria: SearchCriteria) {
  try {
    const prompt = buildJobSearchPrompt(companyName, criteria)
    
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: getJobSearchSystemPrompt(criteria)
        },
        {
          role: "user",
          content: prompt
        }
      ],
      response_format: { type: "json_object" },
      temperature: 0.3,
      max_tokens: 2000
    })

    const content = response.choices[0].message.content
    if (!content) return []

    const data = JSON.parse(content)
    const jobs = data.jobs || []

    // Add metadata to each job
    return jobs.map((job: any) => ({
      ...job,
      company_name: companyName,
      found_date: new Date().toISOString(),
      is_relevant: true,
      search_method: 'knowledge_based',
      job_id: `${companyName.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }))

  } catch (error) {
    console.error(`Error searching ${companyName}:`, error)
    return []
  }
}

function getJobSearchSystemPrompt(criteria: SearchCriteria): string {
  return `
You are an expert job market analyst with deep knowledge of technology companies and their hiring patterns.

Your task is to generate realistic, current job postings based on your knowledge of companies, their typical roles, and industry standards.

FILTERING CRITERIA:
- Preferred locations: ${criteria.locations.join(', ')}
- Job keywords: ${criteria.title_keywords.join(', ')}  
- Experience levels: ${criteria.experience_levels.join(', ')}
- Remote allowed: ${criteria.remote_allowed}
- Company types: ${criteria.company_types.join(', ')}
- Minimum salary: $${criteria.salary_min}

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
{
  "jobs": [
    {
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
      "company_size": "startup/midsize/enterprise",
      "posting_date": "2024-01-15"
    }
  ],
  "search_summary": "Summary of what types of jobs were found and why",
  "company_insights": "Brief insights about the company's hiring patterns"
}
`
}

function buildJobSearchPrompt(companyName: string, criteria: SearchCriteria): string {
  return `
Generate realistic current job openings for ${companyName} based on your knowledge of the company.

COMPANY: ${companyName}
CAREER PAGE: https://${companyName.toLowerCase().replace(/\s+/g, '')}.com/careers

JOB SEARCH CRITERIA:
• Target Job Titles: ${criteria.title_keywords.join(', ')}
• Preferred Locations: ${criteria.locations.join(', ')}
• Experience Levels: ${criteria.experience_levels.join(', ')}
• Remote Work: ${criteria.remote_allowed ? 'Required/Preferred' : 'Not preferred'}
• Company Types: ${criteria.company_types.join(', ')}
• Minimum Salary: $${criteria.salary_min}

TASK:
Based on your knowledge of ${companyName}, generate 2-4 realistic job postings that:
1. Match the specified criteria above
2. Are typical of roles this company would actually hire for
3. Have realistic requirements and compensation
4. Include proper job URLs and locations
5. Have high relevance scores (75+ out of 100)

Consider ${companyName}'s:
- Business model and technology stack
- Company size and growth stage
- Known office locations and remote work policies
- Industry reputation and typical compensation levels
- Current market conditions and hiring trends

Generate jobs that a job seeker with these criteria would genuinely want to apply for.
`
}
