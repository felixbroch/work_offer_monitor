import { NextRequest, NextResponse } from 'next/server'

// This is a Next.js API route that proxies requests to the Python backend
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000'
  
  try {
    const params = new URLSearchParams(searchParams)
    const response = await fetch(`${backendUrl}/api/jobs?${params}`)
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('API Error:', error)
    
    // Provide mock data when backend is unavailable
    const mockJobs = {
      jobs: [
        {
          id: 1,
          title: 'Senior Software Engineer',
          company: 'Tech Corp',
          location: 'San Francisco, CA',
          remote: true,
          salary: '$120,000 - $180,000',
          date_posted: '2024-01-15',
          source: 'indeed',
          url: 'https://example.com/job1',
          description: 'Looking for an experienced software engineer...',
          experience_level: 'senior'
        },
        {
          id: 2,
          title: 'Frontend Developer',
          company: 'StartupXYZ',
          location: 'New York, NY',
          remote: false,
          salary: '$80,000 - $120,000',
          date_posted: '2024-01-14',
          source: 'github',
          url: 'https://example.com/job2',
          description: 'Join our frontend team...',
          experience_level: 'mid-level'
        }
      ],
      total: 2,
      message: 'Mock data - backend unavailable'
    }
    
    return NextResponse.json(mockJobs)
  }
}

export async function POST(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000'
  
  try {
    const body = await request.json()
    const response = await fetch(`${backendUrl}/api/jobs/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Search failed')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Search failed' },
      { status: 500 }
    )
  }
}
