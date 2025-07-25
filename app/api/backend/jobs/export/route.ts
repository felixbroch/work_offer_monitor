import { NextResponse } from 'next/server'

export async function POST(request: any) {
  try {
    const body = await request.json()
    const { format = 'csv', jobs = [] } = body

    if (!jobs || jobs.length === 0) {
      return NextResponse.json(
        { error: 'No jobs to export' },
        { status: 400 }
      )
    }

    if (format === 'csv') {
      // Generate CSV content
      const headers = ['Title', 'Company', 'Location', 'Remote', 'Salary', 'URL', 'Date Posted', 'Source']
      const csvRows = [headers.join(',')]
      
      jobs.forEach((job: any) => {
        const row = [
          `"${job.title || ''}"`,
          `"${job.company || ''}"`,
          `"${job.location || ''}"`,
          job.remote ? 'Yes' : 'No',
          `"${job.salary || 'Not specified'}"`,
          `"${job.url || ''}"`,
          `"${job.date_posted || ''}"`,
          `"${job.source || ''}"`
        ]
        csvRows.push(row.join(','))
      })

      const csvContent = csvRows.join('\n')
      
      return new Response(csvContent, {
        status: 200,
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': 'attachment; filename=jobs-export.csv'
        }
      })
    }

    if (format === 'json') {
      return NextResponse.json({
        jobs,
        exported_at: new Date().toISOString(),
        total_jobs: jobs.length
      })
    }

    return NextResponse.json(
      { error: 'Unsupported format. Use csv or json' },
      { status: 400 }
    )

  } catch (error) {
    console.error('Export error:', error)
    return NextResponse.json(
      { error: 'Failed to export jobs' },
      { status: 500 }
    )
  }
}
