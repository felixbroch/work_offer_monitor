export function GET() {
  // Mock company data for dashboard
  const companies = [
    {
      id: 1,
      name: 'Tech Corp',
      domain: 'techcorp.com',
      industry: 'Technology',
      size: 'Large',
      jobs_posted: 15,
      last_activity: '2024-01-15',
      status: 'active'
    },
    {
      id: 2,
      name: 'StartupXYZ',
      domain: 'startupxyz.com', 
      industry: 'Fintech',
      size: 'Small',
      jobs_posted: 3,
      last_activity: '2024-01-10',
      status: 'active'
    },
    {
      id: 3,
      name: 'Enterprise Solutions',
      domain: 'enterprise-sol.com',
      industry: 'Consulting',
      size: 'Medium',
      jobs_posted: 8,
      last_activity: '2024-01-12',
      status: 'inactive'
    }
  ]

  return Response.json({
    companies,
    total: companies.length,
    active: companies.filter(c => c.status === 'active').length
  })
}

export function POST(request: Request) {
  return request.json().then(body => {
    const { name, domain, industry, size } = body

    // Validate required fields
    if (!name || !domain) {
      return Response.json(
        { error: 'Name and domain are required' },
        { status: 400 }
      )
    }

    // Mock creating a new company
    const newCompany = {
      id: Date.now(),
      name,
      domain,
      industry: industry || 'Unknown',
      size: size || 'Unknown',
      jobs_posted: 0,
      last_activity: new Date().toISOString().split('T')[0],
      status: 'active'
    }

    return Response.json(newCompany, { status: 201 })
  }).catch(error => {
    console.error('Create company error:', error)
    return Response.json(
      { error: 'Failed to create company' },
      { status: 500 }
    )
  })
}
