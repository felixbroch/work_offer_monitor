export async function POST(request: Request) {
  console.log('🔄 [SEARCH-API] Starting job search request...')
  
  try {
    // Parse request body
    const body = await request.json().catch(err => {
      console.error('❌ [SEARCH-API] JSON parse error:', err)
      return {}
    })
    
    console.log('📥 [SEARCH-API] Request received:', {
      hasApiKey: !!body.api_key,
      companiesCount: body.companies?.length || 0,
      hasCriteria: !!body.criteria,
      apiKeyPrefix: body.api_key?.substring(0, 10) + '...'
    })
    
    // Validate required fields
    if (!body.api_key) {
      console.warn('❌ [SEARCH-API] Missing API key')
      return Response.json(
        { success: false, error: 'API key is required' },
        { status: 400 }
      )
    }

    if (!body.companies || body.companies.length === 0) {
      console.warn('❌ [SEARCH-API] Missing companies')
      return Response.json(
        { success: false, error: 'At least one company is required' },
        { status: 400 }
      )
    }

    console.log('✅ [SEARCH-API] Validation passed, calling OpenAI...')

    // Try OpenAI integration with proper error handling
    try {
      // Dynamic import of OpenAI
      const { OpenAI } = await import('openai')
      const openai = new OpenAI({ apiKey: body.api_key })
      
      console.log('🤖 [SEARCH-API] OpenAI client initialized')
      
      // Generate jobs for the first company as a test
      const testCompany = body.companies[0]
      const criteria = body.criteria || {}
      
      console.log('📝 [SEARCH-API] Generating jobs for:', testCompany)
      
      const prompt = `Generate 2-3 realistic job postings for ${testCompany} that match these criteria:
      
Location preferences: ${criteria.locations?.join(', ') || 'Any'}
Job titles: ${criteria.title_keywords?.join(', ') || 'Software Engineer, Developer'}
Experience levels: ${criteria.experience_levels?.join(', ') || 'mid-level, senior'}
Remote work: ${criteria.remote_allowed ? 'Yes' : 'Flexible'}

Return JSON format:
{
  "jobs": [
    {
      "title": "job title",
      "company_name": "${testCompany}",
      "location": "location",
      "url": "https://careers.${testCompany.toLowerCase()}.com/job-id",
      "description": "brief description",
      "experience_level": "level",
      "salary_range": "$X-Y",
      "posting_date": "2024-01-15",
      "search_method": "AI_GENERATED",
      "job_id": "unique-id"
    }
  ]
}`

      const response = await openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are a job market expert. Generate realistic job postings in JSON format.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        response_format: { type: 'json_object' },
        temperature: 0.3,
        max_tokens: 1500
      })

      console.log('🎯 [SEARCH-API] OpenAI response received')
      
      const content = response.choices[0]?.message?.content
      if (!content) {
        throw new Error('No content in OpenAI response')
      }

      const jobData = JSON.parse(content)
      const jobs = jobData.jobs || []
      
      console.log('✅ [SEARCH-API] Successfully generated jobs:', jobs.length)

      return Response.json({
        success: true,
        jobs: jobs,
        companies_searched: body.companies.length,
        companies_with_results: jobs.length > 0 ? 1 : 0,
        search_method: 'OPENAI_INTEGRATION',
        total_jobs: jobs.length,
        timestamp: new Date().toISOString(),
        debug_info: {
          api_key_valid: true,
          openai_called: true,
          prompt_length: prompt.length,
          response_length: content.length
        }
      })

    } catch (openaiError) {
      console.error('❌ [SEARCH-API] OpenAI error:', openaiError)
      
      // Fallback to mock data
      const mockJobs = [
        {
          title: 'Senior Software Engineer',
          company_name: body.companies[0],
          location: body.criteria?.locations?.[0] || 'San Francisco, CA',
          url: `https://careers.${body.companies[0].toLowerCase().replace(/\s+/g, '')}.com/job1`,
          description: 'Build scalable applications using modern technologies...',
          experience_level: 'senior',
          salary_range: '$140k-180k',
          posting_date: '2024-01-15',
          search_method: 'MOCK_FALLBACK',
          job_id: `mock-${Date.now()}-1`
        },
        {
          title: 'Frontend Developer',
          company_name: body.companies[0],
          location: 'Remote',
          url: `https://careers.${body.companies[0].toLowerCase().replace(/\s+/g, '')}.com/job2`,
          description: 'Create beautiful user interfaces with React and TypeScript...',
          experience_level: 'mid-level',
          salary_range: '$100k-140k',
          posting_date: '2024-01-14',
          search_method: 'MOCK_FALLBACK',
          job_id: `mock-${Date.now()}-2`
        }
      ]

      return Response.json({
        success: true,
        jobs: mockJobs,
        companies_searched: body.companies.length,
        companies_with_results: 1,
        search_method: 'MOCK_FALLBACK',
        total_jobs: mockJobs.length,
        timestamp: new Date().toISOString(),
        debug_info: {
          api_key_valid: !!body.api_key,
          openai_called: false,
          openai_error: openaiError instanceof Error ? openaiError.message : 'Unknown error',
          fallback_used: true
        }
      })
    }

  } catch (error) {
    console.error('❌ [SEARCH-API] Fatal error:', error)
    
    return Response.json({
      success: false,
      error: error instanceof Error ? error.message : 'Internal server error',
      jobs: [],
      search_method: 'ERROR',
      timestamp: new Date().toISOString(),
      debug_info: {
        error_type: error instanceof Error ? error.constructor.name : 'Unknown',
        error_message: error instanceof Error ? error.message : 'Unknown error'
      }
    }, { status: 500 })
  }
}

// Add OPTIONS handler for CORS
export async function OPTIONS() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  })
}
