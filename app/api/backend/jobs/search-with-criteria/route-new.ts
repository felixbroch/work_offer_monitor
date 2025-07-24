export async function POST(request: any) {
  console.log('🔄 Starting search-with-criteria API call...')
  
  try {
    const { NextResponse } = await eval('import("next/server")')
    const body = await request.json()
    
    console.log('📥 Received search request:', {
      hasApiKey: !!body.api_key,
      companiesCount: body.companies?.length || 0,
      hasCriteria: !!body.criteria
    })
    
    // Validate required fields
    if (!body.api_key) {
      console.warn('❌ Missing API key')
      return NextResponse.json(
        { success: false, error: 'API key is required' },
        { status: 400 }
      )
    }

    if (!body.companies || body.companies.length === 0) {
      console.warn('❌ Missing companies')
      return NextResponse.json(
        { success: false, error: 'At least one company is required' },
        { status: 400 }
      )
    }

    // For now, return mock data to ensure the endpoint works
    console.log('✅ Returning mock job data...')
    
    const mockJobs = [
      {
        title: 'Senior Frontend Developer',
        company_name: body.companies[0],
        location: body.criteria?.locations?.[0] || 'San Francisco, CA',
        url: `https://${body.companies[0].toLowerCase().replace(/\s+/g, '')}.com/careers/frontend-dev`,
        description: 'Build modern web applications using React, TypeScript, and cutting-edge frontend technologies...',
        experience_level: 'senior',
        department: 'Engineering',
        relevance_score: 92,
        salary_range: '$140k-180k',
        key_skills: ['React', 'TypeScript', 'JavaScript', 'CSS'],
        remote_friendly: true,
        company_size: 'midsize',
        posting_date: '2024-01-15',
        search_method: 'MOCK_DATA',
        job_id: `mock-${Date.now()}-1`,
        source: 'company_careers'
      },
      {
        title: 'Backend Engineer',
        company_name: body.companies[0],
        location: body.criteria?.locations?.[0] || 'Remote',
        url: `https://${body.companies[0].toLowerCase().replace(/\s+/g, '')}.com/careers/backend-eng`,
        description: 'Design and build scalable backend systems using modern technologies...',
        experience_level: 'mid-level',
        department: 'Engineering',
        relevance_score: 88,
        salary_range: '$120k-160k',
        key_skills: ['Node.js', 'Python', 'PostgreSQL', 'AWS'],
        remote_friendly: true,
        company_size: 'midsize',
        posting_date: '2024-01-14',
        search_method: 'MOCK_DATA',
        job_id: `mock-${Date.now()}-2`,
        source: 'company_careers'
      }
    ]

    const response = {
      success: true,
      jobs: mockJobs,
      companies_searched: body.companies.length,
      companies_with_results: body.companies.length,
      search_method: 'MOCK_DATA_FALLBACK',
      total_jobs: mockJobs.length,
      timestamp: new Date().toISOString(),
      message: 'Mock data returned - API endpoint working correctly'
    }

    console.log('📤 Sending response:', {
      success: response.success,
      jobCount: response.jobs.length,
      searchMethod: response.search_method
    })

    return NextResponse.json(response)

  } catch (error) {
    console.error('❌ Search API error:', error)
    
    // Fallback response without NextResponse import
    const fallbackResponse = {
      success: false,
      error: error instanceof Error ? error.message : 'Internal server error',
      jobs: [],
      search_method: 'ERROR_FALLBACK',
      timestamp: new Date().toISOString()
    }
    
    return new Response(JSON.stringify(fallbackResponse), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
