export async function POST(request: any) {
  console.log('🔄 TEST: Starting super simple API call...')
  
  try {
    // Use standard Response instead of NextResponse to avoid import issues
    const body = await request.json()
    
    console.log('📥 TEST: Request received:', {
      hasApiKey: !!body.api_key,
      companiesCount: body.companies?.length || 0
    })
    
    // Simple validation
    if (!body.api_key) {
      return new Response(JSON.stringify({
        success: false,
        error: 'API key is required'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      })
    }

    if (!body.companies || body.companies.length === 0) {
      return new Response(JSON.stringify({
        success: false,
        error: 'At least one company is required'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      })
    }

    // Return simple mock data
    const response = {
      success: true,
      jobs: [
        {
          title: 'Test Job 1',
          company_name: body.companies[0] || 'Test Company',
          location: 'San Francisco, CA',
          url: 'https://example.com/job1',
          description: 'This is a test job posting...',
          experience_level: 'senior',
          salary_range: '$100k-150k',
          posting_date: '2024-01-15',
          search_method: 'SIMPLE_TEST',
          job_id: 'test-1'
        },
        {
          title: 'Test Job 2',
          company_name: body.companies[0] || 'Test Company',
          location: 'Remote',
          url: 'https://example.com/job2',
          description: 'Another test job posting...',
          experience_level: 'mid-level',
          salary_range: '$80k-120k',
          posting_date: '2024-01-14',
          search_method: 'SIMPLE_TEST',
          job_id: 'test-2'
        }
      ],
      companies_searched: body.companies?.length || 0,
      companies_with_results: 1,
      search_method: 'SIMPLE_TEST',
      total_jobs: 2,
      timestamp: new Date().toISOString()
    }

    console.log('📤 TEST: Sending response with', response.jobs.length, 'jobs')

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('❌ TEST: API error:', error)
    
    return new Response(JSON.stringify({
      success: false,
      error: error instanceof Error ? error.message : 'Internal server error',
      jobs: [],
      search_method: 'ERROR',
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
