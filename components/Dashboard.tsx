'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface DashboardProps {
  statistics: any
  jobs: any[]
}

const COLORS = {
  new: '#22c55e',
  seen: '#6b7280', 
  modified: '#f59e0b',
  removed: '#ef4444'
}

export default function Dashboard({ statistics, jobs }: DashboardProps) {
  if (!statistics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading dashboard data...</p>
      </div>
    )
  }

  // Prepare chart data
  const statusData = Object.entries(statistics.status_counts || {}).map(([status, count]) => ({
    status: status.charAt(0).toUpperCase() + status.slice(1),
    count,
    color: COLORS[status as keyof typeof COLORS] || '#6b7280'
  }))

  const companyData = Object.entries(statistics.company_counts || {})
    .slice(0, 10)
    .map(([company, count]) => ({
      company: company.length > 20 ? company.substring(0, 20) + '...' : company,
      count
    }))

  // Timeline data (last 30 days)
  const timelineData = jobs
    .filter(job => {
      const jobDate = new Date(job.date_first_seen)
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      return jobDate >= thirtyDaysAgo
    })
    .reduce((acc, job) => {
      const date = new Date(job.date_first_seen).toISOString().split('T')[0]
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {} as Record<string, number>)

  const timelineChartData = Object.entries(timelineData)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({
      date: new Date(date).toLocaleDateString('en-GB', { month: 'short', day: 'numeric' }),
      count
    }))

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Jobs</p>
              <p className="text-3xl font-bold text-gray-900">{statistics.total_jobs}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">New Jobs</p>
              <p className="text-3xl font-bold text-success-600">{statistics.status_counts?.new || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Companies</p>
              <p className="text-3xl font-bold text-primary-600">{Object.keys(statistics.company_counts || {}).length}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Recent Activity</p>
              <p className="text-3xl font-bold text-warning-600">{statistics.recent_activity}</p>
              <p className="text-xs text-gray-500">Last 7 days</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Status Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ status, count }) => `${status}: ${count}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Company Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Companies</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={companyData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="company" type="category" width={100} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Timeline Chart */}
      {timelineChartData.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Discovery Timeline (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={timelineChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Jobs */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Jobs</h3>
        <div className="space-y-4">
          {jobs.slice(0, 5).map((job) => (
            <div key={job.job_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{job.job_title}</h4>
                <p className="text-sm text-gray-600">{job.company_name} • {job.location}</p>
                <p className="text-xs text-gray-500">
                  First seen: {new Date(job.date_first_seen).toLocaleDateString('en-GB')}
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`status-${job.status}`}>
                  {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </span>
                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-outline btn-sm"
                  >
                    View Job
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
