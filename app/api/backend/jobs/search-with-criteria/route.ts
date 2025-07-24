export function POST() {
  return Response.json({
    success: true,
    jobs: [{
      title: 'Test Job',
      company_name: 'Test Company',
      location: 'Remote',
      url: 'https://example.com',
      description: 'Test description',
      experience_level: 'senior',
      salary_range: '$100k',
      posting_date: '2024-01-15',
      search_method: 'ULTRA_SIMPLE',
      job_id: 'test-1'
    }],
    total_jobs: 1
  })
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
