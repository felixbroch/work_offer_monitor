import { NextResponse } from 'next/server'

export async function POST(request: any) {
  try {
    const body = await request.json()
    const { query, location, remote, experience_level } = body

    // Mock search results for now
    const mockJobs = [
      {
        id: 1,
        title: 'Senior Software Engineer',
        company: 'Tech Corp',
        location: location || 'San Francisco, CA',
        remote: remote !== undefined ? remote : true,
        salary: '$120,000 - $180,000',
        date_posted: '2024-01-15',
        source: 'indeed',
        url: 'https://example.com/job1',
        description: `Looking for an experienced software engineer with ${query || 'programming'} skills...`,
        experience_level: experience_level || 'senior'
      },
      {
        id: 2,
        title: 'Frontend Developer',
        company: 'StartupXYZ',
        location: location || 'New York, NY',
        remote: remote !== undefined ? remote : false,
        salary: '$80,000 - $120,000',
        date_posted: '2024-01-14',
        source: 'github',
        url: 'https://example.com/job2',
        description: `Join our frontend team working with ${query || 'React'} technology...`,
        experience_level: experience_level || 'mid-level'
      }
    ]

    return NextResponse.json({
      jobs: mockJobs,
      total: mockJobs.length,
      query: query || '',
      filters: {
        location,
        remote,
        experience_level
      }
    })

  } catch (error) {
    console.error('Job search error:', error)
    return NextResponse.json(
      { error: 'Failed to search jobs' },
      { status: 500 }
    )
  }
}
