export async function GET() {
  return new Response(JSON.stringify({
    status: 'OK',
    message: 'Health check passed',
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}

export async function POST() {
  return new Response(JSON.stringify({
    status: 'OK',
    message: 'POST health check passed',
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
