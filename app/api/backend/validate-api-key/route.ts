export async function POST(request: any) {
  try {
    const { NextResponse } = await eval('import("next/server")')
    const body = await request.json()
    const { api_key } = body

    // Basic API key validation
    if (!api_key) {
      return NextResponse.json(
        { valid: false, message: 'API key is required' },
        { status: 400 }
      )
    }

    // Check if it's a valid OpenAI API key format
    if (!api_key.startsWith('sk-') || api_key.length < 20) {
      return NextResponse.json(
        { valid: false, message: 'Invalid API key format. Must start with sk- and be at least 20 characters.' },
        { status: 400 }
      )
    }

    // For now, just validate format - could test with actual OpenAI call later
    return NextResponse.json({
      valid: true,
      message: 'API key format is valid'
    })

  } catch (error) {
    console.error('API key validation error:', error)
    const { NextResponse } = await eval('import("next/server")')
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
