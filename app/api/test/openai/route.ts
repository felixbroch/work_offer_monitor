import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  console.log('🧪 [OPENAI-TEST] Starting OpenAI connection test...')
  
  try {
    const body = await request.json()
    const { api_key } = body

    if (!api_key) {
      return NextResponse.json({
        success: false,
        error: 'API key is required for testing'
      }, { status: 400 })
    }

    console.log('🔑 [OPENAI-TEST] API key provided, testing connection...')

    // Test OpenAI connection
    const { OpenAI } = await import('openai')
    const openai = new OpenAI({ apiKey: api_key })

    // Simple test query
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "user",
          content: "Respond with a simple JSON object: {\"status\": \"connected\", \"message\": \"OpenAI API is working\"}"
        }
      ],
      max_tokens: 100,
      temperature: 0,
      response_format: { type: "json_object" }
    })

    const responseText = completion.choices[0]?.message?.content
    console.log('✅ [OPENAI-TEST] OpenAI response:', responseText)

    return NextResponse.json({
      success: true,
      openai_connected: true,
      response: responseText,
      model_used: "gpt-4o-mini",
      test_timestamp: new Date().toISOString()
    })

  } catch (error: any) {
    console.error('❌ [OPENAI-TEST] Connection failed:', error)
    
    return NextResponse.json({
      success: false,
      openai_connected: false,
      error: error.message || 'Unknown error',
      error_type: error.name || 'Error',
      test_timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'openai-test',
    description: 'Test OpenAI API connectivity',
    usage: 'POST with { "api_key": "your_openai_key" }',
    status: 'ready'
  })
}
