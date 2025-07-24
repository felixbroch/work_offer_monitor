export async function POST(request: any) {
  // Absolute minimal version for debugging
  console.log('🔄 MINIMAL: API called')
  
  try {
    console.log('📥 MINIMAL: Parsing request...')
    const body = await request.json().catch(() => ({}))
    
    console.log('✅ MINIMAL: Request parsed, sending response...')
    
    // Hardcoded response to eliminate all variables
    const hardcodedResponse = {
      success: true,
      jobs: [
        {
          title: 'Software Engineer',
          company_name: 'Test Company',
          location: 'San Francisco, CA',
          url: 'https://example.com/job',
          description: 'Test job description',
          experience_level: 'senior',
          salary_range: '$100k-150k',
          posting_date: '2024-01-15',
          search_method: 'MINIMAL_TEST',
          job_id: 'minimal-test-1'
        }
      ],
      total_jobs: 1,
      timestamp: new Date().toISOString()
    }

    console.log('📤 MINIMAL: Returning response')
    
    return new Response(JSON.stringify(hardcodedResponse), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    })

  } catch (error) {
    console.error('❌ MINIMAL: Error:', error)
    
    return new Response(JSON.stringify({
      success: false,
      error: 'Minimal test failed: ' + (error instanceof Error ? error.message : 'Unknown error'),
      jobs: []
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    })
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
