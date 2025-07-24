'use client'

import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, XCircle, Settings, Plus, Search, Download, RefreshCw, Target } from 'lucide-react'
import ApiKeyModal from '../components/ApiKeyModal'
import JobCriteriaModal from '../components/JobCriteriaModal'
import JobSearch from '../components/JobSearch'
import JobList from '../components/JobList'
import Dashboard from '../components/Dashboard'
import CompanyManager from '../components/CompanyManager'

interface JobStatistics {
  total_jobs: number
  status_counts: Record<string, number>
  company_counts: Record<string, number>
  recent_activity: number
  new_jobs_today: number
}

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

export default function Home() {
  const [apiKey, setApiKey] = useState<string>('')
  const [showApiKeyModal, setShowApiKeyModal] = useState(false)
  const [showCriteriaModal, setShowCriteriaModal] = useState(false)
  const [jobCriteria, setJobCriteria] = useState({
    locations: ['Remote', 'New York', 'San Francisco'],
    title_keywords: ['Software Engineer', 'Developer', 'Data Scientist'],
    experience_levels: ['junior', 'mid-level', 'senior'],
    remote_allowed: true,
    company_types: ['Startup', 'Enterprise', 'Tech Company']
  })
  const [currentView, setCurrentView] = useState<'dashboard' | 'jobs' | 'search' | 'companies'>('dashboard')
  const [jobs, setJobs] = useState<Job[]>([])
  const [statistics, setStatistics] = useState<JobStatistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check for API key on component mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem('openai_api_key')
    if (savedApiKey) {
      setApiKey(savedApiKey)
    } else {
      setShowApiKeyModal(true)
    }
  }, [])

  // Load initial data when API key is available
  useEffect(() => {
    if (apiKey) {
      loadJobs()
      loadStatistics()
    }
  }, [apiKey])

  const handleApiKeySubmit = (key: string) => {
    setApiKey(key)
    localStorage.setItem('openai_api_key', key)
    setShowApiKeyModal(false)
    loadJobs()
    loadStatistics()
  }

  const handleCriteriaSubmit = (criteria: any) => {
    setJobCriteria(criteria)
    localStorage.setItem('job_criteria', JSON.stringify(criteria))
    setShowCriteriaModal(false)
  }

  // Load saved criteria on mount
  useEffect(() => {
    const savedCriteria = localStorage.getItem('job_criteria')
    if (savedCriteria) {
      try {
        setJobCriteria(JSON.parse(savedCriteria))
      } catch (e) {
        console.error('Error loading saved criteria:', e)
      }
    }
  }, [])

  const loadJobs = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/backend/jobs')
      if (!response.ok) throw new Error('Failed to load jobs')
      const data = await response.json()
      setJobs(data.jobs || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await fetch('/api/backend/jobs/statistics')
      if (!response.ok) throw new Error('Failed to load statistics')
      const data = await response.json()
      setStatistics(data)
    } catch (err) {
      console.error('Failed to load statistics:', err)
    }
  }

  const handleRefresh = () => {
    loadJobs()
    loadStatistics()
  }

  const handleJobSearch = async (companies: Array<{ company_name: string; career_page_url?: string }>) => {
    try {
      setLoading(true)
      const response = await fetch('/api/backend/jobs/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          companies,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Search failed')
      }

      const data = await response.json()
      
      // Refresh data after successful search
      await loadJobs()
      await loadStatistics()
      
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const handleExportJobs = async () => {
    try {
      const response = await fetch('/api/backend/jobs/export')
      if (!response.ok) throw new Error('Failed to export jobs')
      const data = await response.json()
      
      // Create and download CSV file
      const blob = new Blob([data.csv_data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = data.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export jobs')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new':
        return <CheckCircle className="h-4 w-4 text-success-600" />
      case 'modified':
        return <AlertCircle className="h-4 w-4 text-warning-600" />
      case 'removed':
        return <XCircle className="h-4 w-4 text-danger-600" />
      default:
        return <CheckCircle className="h-4 w-4 text-gray-600" />
    }
  }

  if (!apiKey && !showApiKeyModal) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-center mb-4">Job Search Assistant</h1>
          <p className="text-gray-600 text-center mb-6">
            Please configure your OpenAI API key to get started.
          </p>
          <button
            onClick={() => setShowApiKeyModal(true)}
            className="btn-primary w-full"
          >
            Configure API Key
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Job Search Assistant</h1>
              {statistics && (
                <div className="ml-8 flex items-center space-x-4 text-sm text-gray-600">
                  <span className="flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    {statistics.total_jobs} total jobs
                  </span>
                  <span className="flex items-center">
                    {getStatusIcon('new')}
                    <span className="ml-1">{statistics.status_counts?.new || 0} new</span>
                  </span>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefresh}
                className="btn-secondary flex items-center"
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleExportJobs}
                className="btn-outline flex items-center"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
              <button
                onClick={() => setShowCriteriaModal(true)}
                className="btn-primary flex items-center"
              >
                <Target className="h-4 w-4 mr-2" />
                Job Criteria
              </button>
              <button
                onClick={() => setShowApiKeyModal(true)}
                className="btn-secondary flex items-center"
              >
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { key: 'dashboard', label: 'Dashboard', icon: CheckCircle },
              { key: 'jobs', label: 'Jobs', icon: Search },
              { key: 'search', label: 'Search', icon: Plus },
              { key: 'companies', label: 'Companies', icon: Settings },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setCurrentView(key as any)}
                className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                  currentView === key
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Error Display */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-danger-50 border border-danger-200 rounded-md p-4">
            <div className="flex">
              <XCircle className="h-5 w-5 text-danger-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-danger-800">Error</h3>
                <p className="mt-1 text-sm text-danger-700">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-sm text-danger-600 hover:text-danger-500"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' && (
          <Dashboard statistics={statistics} jobs={jobs} />
        )}
        {currentView === 'jobs' && (
          <JobList jobs={jobs} loading={loading} />
        )}
        {currentView === 'search' && (
          <JobSearch 
            onSearch={handleJobSearch} 
            loading={loading} 
            apiKey={apiKey}
            jobCriteria={jobCriteria}
          />
        )}
        {currentView === 'companies' && (
          <CompanyManager />
        )}
      </main>

      {/* API Key Modal */}
      {showApiKeyModal && (
        <ApiKeyModal
          onSubmit={handleApiKeySubmit}
          onClose={() => setShowApiKeyModal(false)}
          initialKey={apiKey}
        />
      )}

      {/* Job Criteria Modal */}
      {showCriteriaModal && (
        <JobCriteriaModal
          onSubmit={handleCriteriaSubmit}
          onClose={() => setShowCriteriaModal(false)}
          initialCriteria={jobCriteria}
        />
      )}
    </div>
  )
}
