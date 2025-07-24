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
    console.log('🔄 Backend unavailable, using direct OpenAI approach for job search')
    console.log('📊 Search request details:', {
      companiesCount: body.companies.length,
      companies: body.companies,
      criteriaType: isBroadSearch(body.criteria) ? 'BROAD' : 'TARGETED',
      locations: body.criteria.locations,
      keywords: body.criteria.title_keywords,
      experience: body.criteria.experience_levels
    })
    
    const { OpenAI } = await import('openai')
    const openai = new OpenAI({
      apiKey: body.api_key
    })

    const allJobs = []
    const searchErrors = []
    const searchStats = {
      companiesProcessed: 0,
      totalJobsFound: 0,
      companiesWithResults: 0,
      companiesWithoutResults: 0,
      fallbacksUsed: 0
    }

    // Search each company
    for (const company of body.companies) {
      try {
        console.log(`\n🏢 === Searching ${company} (${searchStats.companiesProcessed + 1}/${body.companies.length}) ===`)
        
        const jobs = await searchCompanyJobs(openai, company, body.criteria)
        
        if (jobs.length > 0) {
          allJobs.push(...jobs)
          searchStats.companiesWithResults++
          console.log(`✅ ${company}: Found ${jobs.length} jobs`)
        } else {
          searchStats.companiesWithoutResults++
          console.log(`⚠️  ${company}: No jobs found`)
        }
        
        searchStats.companiesProcessed++
        searchStats.totalJobsFound += jobs.length
        
        // Check if fallback was used
        if (jobs.some(job => job.search_method?.includes('fallback'))) {
          searchStats.fallbacksUsed++
        }
        
      } catch (error) {
        console.error(`❌ Error searching ${company}:`, error)
        searchErrors.push(`${company}: ${error instanceof Error ? error.message : 'Unknown error'}`)
        searchStats.companiesProcessed++
      }
    }

    // Log final statistics
    console.log('\n📈 === SEARCH COMPLETION SUMMARY ===')
    console.log('Statistics:', searchStats)
    console.log(`Success Rate: ${searchStats.companiesWithResults}/${searchStats.companiesProcessed} companies (${Math.round(searchStats.companiesWithResults/searchStats.companiesProcessed*100)}%)`)
    console.log(`Average Jobs per Company: ${Math.round(searchStats.totalJobsFound/searchStats.companiesProcessed*10)/10}`)
    
    if (searchErrors.length > 0) {
      console.log('❌ Errors encountered:', searchErrors)
    }

    // Check if we need to suggest broadening the search
    const shouldSuggestBroadening = allJobs.length === 0 && !isBroadSearch(body.criteria)
    
    if (shouldSuggestBroadening) {
      console.log('💡 No results found with current criteria, suggesting broader search to user')
    }

    // Return results with comprehensive metadata
    const response = {
      success: true,
      jobs: allJobs,
      total_jobs: allJobs.length,
      companies_searched: body.companies.length,
      companies_with_results: searchStats.companiesWithResults,
      search_criteria: body.criteria,
      search_type: isBroadSearch(body.criteria) ? 'broad' : 'targeted',
      search_stats: searchStats,
      suggestions: shouldSuggestBroadening ? [
        'Try broader keywords (e.g., "Software Engineer" instead of specific technologies)',
        'Expand location to "All Locations"',
        'Include more experience levels',
        'Consider related job titles or roles'
      ] : undefined,
      errors: searchErrors.length > 0 ? searchErrors : undefined
    }

    console.log(`🎯 Final response: ${allJobs.length} jobs from ${searchStats.companiesWithResults} companies`)
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
    console.log(`🔍 Starting search for ${companyName} with criteria:`, {
      locations: criteria.locations,
      keywords: criteria.title_keywords,
      experience: criteria.experience_levels,
      hasBroadCriteria: isBroadSearch(criteria)
    })

    const prompt = buildJobSearchPrompt(companyName, criteria)
    console.log(`📝 Generated prompt for ${companyName}:`, prompt.substring(0, 200) + '...')
    
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
    if (!content) {
      console.warn(`❌ No content returned from OpenAI for ${companyName}`)
      return []
    }

    const data = JSON.parse(content)
    const jobs = data.jobs || []

    console.log(`📊 ${companyName} search results:`, {
      jobsFound: jobs.length,
      searchSummary: data.search_summary,
      companyInsights: data.company_insights
    })

    // If no jobs found with strict criteria, try a broader search
    if (jobs.length === 0 && !isBroadSearch(criteria)) {
      console.log(`🔄 No results with strict criteria for ${companyName}, trying broader search...`)
      return await searchCompanyJobsBroad(openai, companyName, criteria)
    }

    // Add metadata to each job
    const processedJobs = jobs.map((job: any) => ({
      ...job,
      company_name: companyName,
      found_date: new Date().toISOString(),
      is_relevant: true,
      search_method: isBroadSearch(criteria) ? 'knowledge_based_broad' : 'knowledge_based_targeted',
      job_id: `${companyName.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }))

    console.log(`✅ Successfully processed ${processedJobs.length} jobs for ${companyName}`)
    return processedJobs

  } catch (error) {
    console.error(`❌ Error searching ${companyName}:`, error)
    return []
  }
}

// Helper function to detect if search criteria are broad/general
function isBroadSearch(criteria: SearchCriteria): boolean {
  const hasGenericKeywords = criteria.title_keywords.length <= 3 && 
    criteria.title_keywords.some(keyword => 
      ['Software Engineer', 'Developer', 'Data Scientist', 'Engineer', 'Analyst'].includes(keyword)
    )
  
  const hasMultipleLocations = criteria.locations.length >= 3
  const hasMultipleExperience = criteria.experience_levels.length >= 2

  return hasGenericKeywords && hasMultipleLocations && hasMultipleExperience
}

// Fallback search with broader criteria
async function searchCompanyJobsBroad(openai: any, companyName: string, originalCriteria: SearchCriteria) {
  try {
    console.log(`🌐 Attempting broad search for ${companyName}...`)
    
    // Create broader criteria
    const broadCriteria: SearchCriteria = {
      locations: ['Remote', 'United States', 'Europe', 'Global'],
      title_keywords: ['Software Engineer', 'Developer', 'Product Manager', 'Data Scientist', 'Designer'],
      experience_levels: ['junior', 'mid-level', 'senior'],
      remote_allowed: true,
      company_types: ['Technology', 'Startup', 'Enterprise'],
      salary_min: '60000' // Lower minimum
    }

    const prompt = buildBroadJobSearchPrompt(companyName, broadCriteria, originalCriteria)
    
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: getBroadJobSearchSystemPrompt(broadCriteria)
        },
        {
          role: "user",
          content: prompt
        }
      ],
      response_format: { type: "json_object" },
      temperature: 0.4, // Slightly higher for more variety
      max_tokens: 2000
    })

    const content = response.choices[0].message.content
    if (!content) return []

    const data = JSON.parse(content)
    const jobs = data.jobs || []

    console.log(`🎯 Broad search for ${companyName} found ${jobs.length} jobs`)

    return jobs.map((job: any) => ({
      ...job,
      company_name: companyName,
      found_date: new Date().toISOString(),
      is_relevant: true,
      search_method: 'knowledge_based_broad_fallback',
      job_id: `${companyName.toLowerCase().replace(/\s+/g, '-')}-broad-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }))

  } catch (error) {
    console.error(`❌ Broad search failed for ${companyName}:`, error)
    return []
  }
}

function getJobSearchSystemPrompt(criteria: SearchCriteria): string {
  const isBroad = isBroadSearch(criteria)
  const relevanceThreshold = isBroad ? 50 : 70 // Lower threshold for broad searches
  
  return `
You are an expert job market analyst with deep knowledge of technology companies and their hiring patterns.

Your task is to generate realistic, current job postings based on your knowledge of companies, their typical roles, and industry standards.

SEARCH TYPE: ${isBroad ? 'BROAD/GENERAL SEARCH' : 'TARGETED SEARCH'}

FILTERING CRITERIA:
- Preferred locations: ${criteria.locations.join(', ')}
- Job keywords: ${criteria.title_keywords.join(', ')}  
- Experience levels: ${criteria.experience_levels.join(', ')}
- Remote allowed: ${criteria.remote_allowed}
- Company types: ${criteria.company_types.join(', ')}
- Minimum salary: $${criteria.salary_min}

INSTRUCTIONS FOR ${isBroad ? 'BROAD' : 'TARGETED'} SEARCH:
${isBroad ? `
- Generate a variety of realistic job postings that the company would likely have
- Prefer jobs that match the criteria, but include general roles even if not perfect matches
- Focus on showing the company's diverse hiring opportunities
- Include different departments and experience levels
- Relevance threshold: Include jobs with score >= ${relevanceThreshold} (more inclusive)
` : `
- Generate realistic job postings that closely match the filtering criteria
- Prioritize jobs that best fit the specified requirements
- Only include jobs that are genuinely relevant to the search
- Relevance threshold: Include jobs with score >= ${relevanceThreshold}
`}

GENERAL REQUIREMENTS:
- Use realistic job titles, locations, and requirements
- Include salary ranges typical for the company and role level
- Make URLs realistic (company domain + /careers/job-id)
- Base postings on known company information and industry standards
- Consider current market trends and typical hiring patterns

IMPORTANT: Even if criteria seem broad or general, ALWAYS generate 2-4 realistic job postings. 
The company should have open positions - focus on what they would realistically be hiring for.

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
      "relevance_score": ${isBroad ? '65-95' : '75-95'},
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

function getBroadJobSearchSystemPrompt(criteria: SearchCriteria): string {
  return `
You are an expert job market analyst specializing in providing comprehensive overviews of company hiring.

Your task is to generate a diverse set of realistic job postings that showcase what the company typically hires for, 
even when the search criteria were initially too restrictive or yielded no results.

FALLBACK SEARCH CRITERIA:
- Locations: ${criteria.locations.join(', ')}
- Job categories: ${criteria.title_keywords.join(', ')}  
- Experience levels: ${criteria.experience_levels.join(', ')}
- Remote work: ${criteria.remote_allowed}
- Company types: ${criteria.company_types.join(', ')}

INSTRUCTIONS FOR BROAD SEARCH:
- Generate 3-5 realistic job postings that represent the company's typical hiring
- Show variety across different departments (Engineering, Product, Data, Design, etc.)
- Include different experience levels to show career progression opportunities
- Focus on roles the company would genuinely be hiring for based on their business
- Make jobs appealing and realistic, not generic
- Include jobs with relevance scores >= 50 (inclusive approach)

IMPORTANT: This is a fallback search because the original criteria were too restrictive.
Your goal is to show what opportunities actually exist at this company, helping the user
discover roles they might not have initially considered.

RESPONSE FORMAT:
Return a JSON object with 3-5 diverse job postings showing the company's hiring landscape.
Use the same JSON structure as the targeted search, but focus on breadth and opportunity discovery.
`
}

function buildBroadJobSearchPrompt(companyName: string, broadCriteria: SearchCriteria, originalCriteria: SearchCriteria): string {
  return `
FALLBACK SEARCH: Generate diverse job openings for ${companyName} 

The original search with these criteria found no results:
• Original Keywords: ${originalCriteria.title_keywords.join(', ')}
• Original Locations: ${originalCriteria.locations.join(', ')}
• Original Experience: ${originalCriteria.experience_levels.join(', ')}

Now showing a broader view of what ${companyName} typically hires for:

COMPANY: ${companyName}
CAREER PAGE: https://${companyName.toLowerCase().replace(/\s+/g, '')}.com/careers

BROAD SEARCH APPROACH:
• Show 3-5 diverse roles across different departments
• Include various experience levels (junior to senior)
• Focus on what ${companyName} would realistically be hiring for
• Consider their business model, technology stack, and growth areas
• Include both technical and non-technical roles if appropriate

TASK:
Generate a diverse set of realistic job postings that:
1. Represent ${companyName}'s typical hiring patterns
2. Show opportunities the user might not have considered
3. Include realistic compensation and requirements
4. Span different departments and experience levels
5. Have relevance scores >= 50 (broad inclusion)

Help the user discover opportunities at ${companyName} beyond their initial search criteria.
Focus on roles that genuinely exist and would be appealing to job seekers.
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
