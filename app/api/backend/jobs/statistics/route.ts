import { NextRequest, NextResponse } from 'next/server'

export async function GET() {
  try {
    const { NextResponse } = await eval('import("next/server")')
    // Mock statistics for now - replace with real data when backend is available
    const statistics = {
      total_jobs: 0,
      recent_activity: 0,
      status_counts: {
        'new': 0,
        'applied': 0,
        'rejected': 0,
        'interview': 0
      },
      company_counts: {},
      new_jobs_today: 0
    }

    return NextResponse.json(statistics)
  } catch (error) {
    console.error('Statistics API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch statistics' },
      { status: 500 }
    )
  }
}
