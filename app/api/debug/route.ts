export async function GET() {
  return Response.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    endpoints: {
      'POST /api/backend/jobs/search-with-criteria': 'Job search with OpenAI',
      'GET /api/backend/jobs': 'Basic jobs list',
      'GET/POST /api/backend/companies': 'Companies management',
      'GET /api/health': 'Health check'
    },
    message: 'API debug endpoint working'
  })
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}))
    
    return Response.json({
      status: 'POST OK',
      received_data: {
        keys: Object.keys(body),
        api_key_present: !!body.api_key,
        companies_count: body.companies?.length || 0
      },
      timestamp: new Date().toISOString(),
      message: 'POST debug endpoint working'
    })
  } catch (error) {
    return Response.json({
      status: 'POST ERROR',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}
