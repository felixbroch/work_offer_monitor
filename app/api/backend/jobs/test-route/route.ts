export async function POST() {
  return new Response(JSON.stringify({
    success: true,
    message: 'Test route working',
    jobs: [{
      title: 'Test Job',
      company_name: 'Test Company',
      location: 'Test Location'
    }]
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
