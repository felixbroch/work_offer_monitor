export function POST() {
  return Response.json({
    success: true,
    jobs: [{
      title: 'Test Job',
      company_name: 'Test Company'
    }]
  })
}
