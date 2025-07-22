'use client'

import { useState, useMemo } from 'react'
import { Search, Filter, ExternalLink, Calendar } from 'lucide-react'

interface Job {
  job_id: string
  company_name: string
  job_title: string
  location: string
  url: string
  description?: string
  date_first_seen: string
  date_last_seen: string
  status: string
}

interface JobListProps {
  jobs: Job[]
  loading: boolean
}

export default function JobList({ jobs, loading }: JobListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [companyFilter, setCompanyFilter] = useState<string>('')
  const [sortBy, setSortBy] = useState<'date_first_seen' | 'date_last_seen' | 'company_name' | 'job_title'>('date_last_seen')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Get unique companies and statuses for filters
  const companies = useMemo(() => {
    const uniqueCompanies = [...new Set(jobs.map(job => job.company_name))].sort()
    return uniqueCompanies
  }, [jobs])

  const statuses = useMemo(() => {
    const uniqueStatuses = [...new Set(jobs.map(job => job.status))].sort()
    return uniqueStatuses
  }, [jobs])

  // Filter and sort jobs
  const filteredJobs = useMemo(() => {
    let filtered = jobs.filter(job => {
      const matchesSearch = !searchTerm || 
        job.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.location?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = !statusFilter || job.status === statusFilter
      const matchesCompany = !companyFilter || job.company_name === companyFilter
      
      return matchesSearch && matchesStatus && matchesCompany
    })

    // Sort jobs
    filtered.sort((a, b) => {
      let aValue: string | Date = a[sortBy]
      let bValue: string | Date = b[sortBy]
      
      if (sortBy === 'date_first_seen' || sortBy === 'date_last_seen') {
        aValue = new Date(aValue as string)
        bValue = new Date(bValue as string)
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

    return filtered
  }, [jobs, searchTerm, statusFilter, companyFilter, sortBy, sortOrder])

  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'text-success-600 bg-success-100'
      case 'modified': return 'text-warning-600 bg-warning-100'
      case 'removed': return 'text-danger-600 bg-danger-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-500">Loading jobs...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Job Listings</h2>
        <p className="text-sm text-gray-600 mt-1 sm:mt-0">
          {filteredJobs.length} of {jobs.length} jobs
        </p>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search jobs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input"
          >
            <option value="">All Statuses</option>
            {statuses.map(status => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>

          {/* Company Filter */}
          <select
            value={companyFilter}
            onChange={(e) => setCompanyFilter(e.target.value)}
            className="input"
          >
            <option value="">All Companies</option>
            {companies.map(company => (
              <option key={company} value={company}>
                {company}
              </option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-')
              setSortBy(field as typeof sortBy)
              setSortOrder(order as 'asc' | 'desc')
            }}
            className="input"
          >
            <option value="date_last_seen-desc">Latest First</option>
            <option value="date_first_seen-desc">Newest First</option>
            <option value="company_name-asc">Company A-Z</option>
            <option value="job_title-asc">Title A-Z</option>
          </select>
        </div>

        {/* Clear Filters */}
        {(searchTerm || statusFilter || companyFilter) && (
          <div className="mt-4 pt-4 border-t">
            <button
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('')
                setCompanyFilter('')
              }}
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>

      {/* Job List */}
      <div className="space-y-4">
        {filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Filter className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-500">
              {jobs.length === 0 
                ? "No jobs have been discovered yet. Run a job search to get started."
                : "Try adjusting your filters to see more results."
              }
            </p>
          </div>
        ) : (
          filteredJobs.map((job) => (
            <div key={job.job_id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {job.job_title}
                    </h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600 space-x-4 mb-3">
                    <span className="font-medium">{job.company_name}</span>
                    {job.location && (
                      <>
                        <span>•</span>
                        <span>{job.location}</span>
                      </>
                    )}
                  </div>

                  {job.description && (
                    <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                      {job.description.length > 200 
                        ? `${job.description.substring(0, 200)}...` 
                        : job.description
                      }
                    </p>
                  )}

                  <div className="flex items-center text-xs text-gray-500 space-x-4">
                    <div className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      First seen: {new Date(job.date_first_seen).toLocaleDateString('en-GB')}
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      Last seen: {new Date(job.date_last_seen).toLocaleDateString('en-GB')}
                    </div>
                  </div>
                </div>

                <div className="ml-4 flex-shrink-0">
                  {job.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary flex items-center"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Apply
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Load More (if needed) */}
      {filteredJobs.length > 0 && filteredJobs.length === jobs.length && (
        <div className="text-center py-6">
          <p className="text-sm text-gray-500">Showing all {jobs.length} jobs</p>
        </div>
      )}
    </div>
  )
}
