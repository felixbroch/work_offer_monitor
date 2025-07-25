'use client'

import { useState, useEffect, useCallback } from 'react'
import { Search, Filter, X, MapPin, Briefcase, Type, AlertCircle, Loader2, Calendar, ExternalLink } from 'lucide-react'

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
  experience_level?: string
  department?: string
  relevance_score?: number
  reasoning?: string
  salary_range?: string
  key_skills?: string[]
  remote_friendly?: boolean
}

interface SearchFilters {
  keywords: string
  location: string
  experience_level: string
}

interface JobSearchEngineProps {
  apiKey: string
  onJobsFound?: (jobs: Job[]) => void
}

export default function JobSearchEngine({ apiKey, onJobsFound }: JobSearchEngineProps) {
  // State for filters
  const [filters, setFilters] = useState<SearchFilters>({
    keywords: '',
    location: 'All',
    experience_level: 'All'
  })

  // State for search
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  
  // Debug state for production debugging
  const [debugInfo, setDebugInfo] = useState<any>(null)
  const [showDebug, setShowDebug] = useState(false)

  // State for companies to search
  const [companies, setCompanies] = useState<string[]>([
    'Google', 'Microsoft', 'Apple', 'Meta', 'Amazon', 'Netflix', 'Spotify', 'Stripe'
  ])

  // Filter options
  const locationOptions = [
    { value: 'All', label: 'All Locations' },
    { value: 'Remote', label: '🌐 Remote' },
    { value: 'Paris', label: '🇫🇷 Paris' },
    { value: 'Lyon', label: '🇫🇷 Lyon' },
    { value: 'New York', label: '🇺🇸 New York' },
    { value: 'San Francisco', label: '🇺🇸 San Francisco' },
    { value: 'London', label: '🇬🇧 London' },
    { value: 'Berlin', label: '🇩🇪 Berlin' }
  ]

  const experienceOptions = [
    { value: 'All', label: 'All Levels' },
    { value: 'Internship', label: '🎓 Internship' },
    { value: 'Entry', label: '🌱 Entry Level' },
    { value: 'Mid', label: '⚡ Mid Level' },
    { value: 'Senior', label: '🏆 Senior Level' }
  ]

  // Get active filters for display
  const getActiveFilters = () => {
    const active = []
    if (filters.keywords.trim()) {
      active.push({ type: 'keywords', value: filters.keywords, label: `Keywords: "${filters.keywords}"` })
    }
    if (filters.location !== 'All') {
      active.push({ type: 'location', value: filters.location, label: `Location: ${filters.location}` })
    }
    if (filters.experience_level !== 'All') {
      active.push({ type: 'experience', value: filters.experience_level, label: `Experience: ${filters.experience_level}` })
    }
    return active
  }

  // Clear specific filter
  const clearFilter = (filterType: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: filterType === 'keywords' ? '' : 'All'
    }))
  }

  // Clear all filters
  const clearAllFilters = () => {
    setFilters({
      keywords: '',
      location: 'All',
      experience_level: 'All'
    })
  }

  // Search function
  const handleSearch = useCallback(async () => {
    if (!apiKey) {
      setError('Please configure your OpenAI API key first')
      return
    }

    console.log('🚀 Starting search with filters:', filters)
    setLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      // Build search criteria from filters - IMPROVED FOR BROAD SEARCHES
      const isBroadSearch = filters.location === 'All' && 
                          filters.experience_level === 'All' && 
                          (!filters.keywords.trim() || filters.keywords.trim().length < 3)

      const searchCriteria = {
        locations: filters.location === 'All' ? 
          ['Remote', 'Paris', 'Lyon', 'New York', 'San Francisco', 'London', 'Berlin'] : 
          [filters.location],
        title_keywords: filters.keywords.trim() ? 
          filters.keywords.split(',').map((k: string) => k.trim()).filter((k: string) => k.length > 0) : 
          ['Software Engineer', 'Developer', 'Data Scientist', 'Product Manager', 'Designer'],
        experience_levels: filters.experience_level === 'All' ? 
          ['junior', 'mid-level', 'senior'] : 
          [filters.experience_level.toLowerCase()],
        remote_allowed: true,
        company_types: ['Technology', 'Startup', 'Enterprise'],
        salary_min: '70000' // Lowered for broader results
      }

      console.log('🔍 Search initiated:', {
        isBroadSearch,
        filters,
        searchCriteria,
        companies: companies.length,
        apiKeyPresent: !!apiKey
      })

      // DEBUGGING: Log request details before sending
      const requestPayload = {
        api_key: apiKey ? `${apiKey.substring(0, 10)}...` : 'MISSING',
        criteria: searchCriteria,
        companies: companies
      }
      
      console.log('📤 SENDING REQUEST TO API:', {
        endpoint: '/api/backend/jobs/search-enhanced', // Updated to use enhanced endpoint
        payload: requestPayload,
        companiesCount: companies.length,
        criteriaValid: !!searchCriteria,
        apiKeyPresent: !!apiKey
      })

      // Call the enhanced API endpoint with better OpenAI integration
      const response = await fetch('/api/backend/jobs/search-enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          criteria: searchCriteria,
          companies: companies
        })
      })

      console.log('📡 API response status:', response.status, response.statusText)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ API request failed:', {
          status: response.status,
          statusText: response.statusText,
          errorText: errorText.substring(0, 500)
        })
        throw new Error(`API request failed: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      // COMPREHENSIVE DEBUG: Store debug information for production debugging
      const debugData = {
        timestamp: new Date().toISOString(),
        searchCriteria,
        apiResponse: data,
        responseStructure: {
          hasSuccess: 'success' in data,
          hasJobs: 'jobs' in data,
          successValue: data.success,
          jobsLength: data.jobs?.length || 0,
          jobsType: typeof data.jobs,
          keys: Object.keys(data),
          companiesSearched: data.companies_searched || 0,
          companiesWithResults: data.companies_with_results || 0
        },
        criticalChecks: {
          apiKeyValid: !!apiKey && apiKey.length > 20,
          companiesListValid: Array.isArray(companies) && companies.length > 0,
          responseIsObject: typeof data === 'object',
          hasJobsArray: Array.isArray(data.jobs),
          jobsArrayLength: data.jobs?.length || 0
        }
      }
      setDebugInfo(debugData)
      
      console.log('� DETAILED API RESPONSE ANALYSIS:', {
        responseKeys: Object.keys(data),
        success: data.success,
        jobsCount: data.jobs?.length || 0,
        jobsType: typeof data.jobs,
        jobsIsArray: Array.isArray(data.jobs),
        searchType: data.search_type,
        companiesSearched: data.companies_searched,
        companiesWithResults: data.companies_with_results,
        searchStats: data.search_stats,
        errors: data.errors,
        suggestions: data.suggestions,
        firstJobSample: data.jobs?.[0] || 'NO_JOBS',
        fullResponse: data // Log full response for debugging
      })

      // IMPROVED: Handle different response formats and ensure jobs are displayed
      const jobs = data.jobs || []
      const isSuccess = data.success !== false // Default to true if not explicitly false
      
      console.log('🎯 JOB PROCESSING ANALYSIS:', {
        rawJobsData: data.jobs,
        jobsExtracted: jobs,
        jobsLength: jobs.length,
        isSuccessFlag: isSuccess,
        dataSuccess: data.success,
        companiesSearched: data.companies_searched,
        companiesWithResults: data.companies_with_results,
        processingStep: 'STARTING_JOB_PROCESSING'
      })
      
      if (jobs.length > 0) {
        console.log('✅ JOBS FOUND - Processing for display...')
        
        // Clear any previous errors when jobs are found
        setError(null)
        
        const foundJobs = jobs.map((job: any, index: number) => {
          const processedJob = {
            ...job,
            job_id: job.job_id || `${job.company_name || 'unknown'}-${Date.now()}-${Math.random()}`,
            job_title: job.title || job.job_title || 'Software Engineer', // Map title to job_title
            company_name: job.company_name || 'Unknown Company',
            location: job.location || 'Unknown Location',
            url: job.url || '#',
            description: job.description || 'See job posting for details',
            date_first_seen: job.posting_date || job.found_date || new Date().toISOString().split('T')[0],
            date_last_seen: job.posting_date || job.found_date || new Date().toISOString().split('T')[0],
            status: 'new' // Default status for all new jobs
          }
          
          console.log(`📝 Processing job ${index + 1}:`, {
            originalJob: job,
            processedJob: processedJob,
            hasTitle: !!(job.title || job.job_title),
            hasCompany: !!job.company_name,
            hasLocation: !!job.location
          })
          
          return processedJob
        })

        console.log('🎉 JOBS SUCCESSFULLY PROCESSED:', {
          jobCount: foundJobs.length,
          firstJob: foundJobs[0],
          allJobTitles: foundJobs.map((j: any) => j.job_title),
          processingComplete: true
        })

        setJobs(foundJobs)
        onJobsFound?.(foundJobs)
        
        console.log(`✅ Search successful: ${foundJobs.length} jobs from ${data.companies_with_results || 'unknown'} companies`)
      } else if (isSuccess) {
        // API succeeded but returned no jobs
        const suggestions = data.suggestions || [
          'Try broader keywords like "Engineer" or "Developer"',
          'Expand location to "All Locations"',
          'Include more experience levels',
          'Consider related job titles'
        ]
        
        setJobs([]) // Clear previous jobs
        setError(`No jobs found matching your criteria. Try adjusting your filters:\n• ${suggestions.join('\n• ')}`)
        console.warn('⚠️ API succeeded but returned no jobs')
      } else {
        // API failed
        const errorMsg = data.error || 'No jobs found matching your criteria.'
        console.warn('⚠️ API returned error:', errorMsg)
        setError(errorMsg)
        setJobs([])
      }

    } catch (err) {
      console.error('❌ Search error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to search for jobs. Please try again.'
      setError(`Search failed: ${errorMessage}`)
      setJobs([])
    } finally {
      setLoading(false)
    }
  }, [apiKey, filters, companies, onJobsFound])

  // Auto-search when filters change (debounced)
  useEffect(() => {
    if (!hasSearched) return // Don't auto-search on initial load

    const timeoutId = setTimeout(() => {
      handleSearch()
    }, 500) // 500ms debounce

    return () => clearTimeout(timeoutId)
  }, [filters, handleSearch, hasSearched])

  // Format posting date
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    } catch {
      return 'Recent'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Job Search</h2>
          <p className="text-gray-600">Find opportunities that match your criteria</p>
        </div>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              Search Jobs
            </>
          )}
        </button>
      </div>

      {/* Filters Panel */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Keywords Filter */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Type className="h-4 w-4" />
              Keywords in Job Title
            </label>
            <input
              type="text"
              placeholder="e.g. React, Python, Data Science"
              value={filters.keywords}
              onChange={(e) => setFilters(prev => ({ ...prev, keywords: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Location Filter */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <MapPin className="h-4 w-4" />
              Location
            </label>
            <select
              value={filters.location}
              onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {locationOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Experience Level Filter */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Briefcase className="h-4 w-4" />
              Experience Level
            </label>
            <select
              value={filters.experience_level}
              onChange={(e) => setFilters(prev => ({ ...prev, experience_level: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {experienceOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Active Filters Display */}
        {getActiveFilters().length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Active Filters:</span>
              <button
                onClick={clearAllFilters}
                className="text-sm text-gray-500 hover:text-gray-700 underline"
              >
                Clear all
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {getActiveFilters().map((filter, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {filter.label}
                  <button
                    onClick={() => clearFilter(filter.type)}
                    className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Debug Panel for Production Debugging */}
      {debugInfo && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-700">Debug Information</h4>
            <button
              onClick={() => setShowDebug(!showDebug)}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              {showDebug ? 'Hide' : 'Show'} Debug
            </button>
          </div>
          
          {showDebug && (
            <div className="space-y-2 text-xs">
              <div>
                <strong>Search Time:</strong> {debugInfo.timestamp}
              </div>
              <div>
                <strong>API Response Structure:</strong>
                <pre className="bg-white p-2 rounded mt-1 text-xs overflow-auto">
{JSON.stringify(debugInfo.responseStructure, null, 2)}
                </pre>
              </div>
              <div>
                <strong>Search Criteria:</strong>
                <pre className="bg-white p-2 rounded mt-1 text-xs overflow-auto">
{JSON.stringify(debugInfo.searchCriteria, null, 2)}
                </pre>
              </div>
              <div>
                <strong>Full API Response:</strong>
                <pre className="bg-white p-2 rounded mt-1 text-xs overflow-auto max-h-40">
{JSON.stringify(debugInfo.apiResponse, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-red-800 font-medium">Search Error</h4>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* No Results Message */}
      {hasSearched && !loading && !error && jobs.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertCircle className="h-8 w-8 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-yellow-800 mb-2">No Results Found</h3>
          <p className="text-yellow-700 mb-4">
            No jobs found matching your current filters. Try adjusting your search criteria:
          </p>
          <ul className="text-sm text-yellow-700 text-left max-w-md mx-auto space-y-1 mb-4">
            <li>• Try broader keywords or remove specific terms</li>
            <li>• Expand location to "All Locations"</li>
            <li>• Include more experience levels</li>
            <li>• Check your spelling</li>
          </ul>
          <button
            onClick={() => setShowDebug(true)}
            className="text-sm bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-4 py-2 rounded border"
          >
            🔧 Show Debug Information
          </button>
        </div>
      )}

      {/* COMPREHENSIVE PRODUCTION DEBUG PANEL */}
      {(showDebug || (hasSearched && jobs.length === 0 && !loading)) && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-red-800">🔧 Production Debug Analysis</h3>
            <button
              onClick={() => setShowDebug(!showDebug)}
              className="text-sm text-red-600 hover:text-red-800 underline"
            >
              {showDebug ? 'Hide' : 'Show'} Debug
            </button>
          </div>
          
          <div className="space-y-4 text-sm">
            <div className="bg-white p-4 rounded border">
              <h4 className="font-semibold text-gray-800 mb-2">🎯 CURRENT DISPLAY STATE:</h4>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <strong>Jobs Array Length:</strong> {jobs.length}
                  <br />
                  <strong>Loading State:</strong> {loading ? 'True' : 'False'}
                  <br />
                  <strong>Error State:</strong> {error || 'None'}
                  <br />
                  <strong>Has Searched:</strong> {hasSearched ? 'True' : 'False'}
                </div>
                <div>
                  <strong>Debug Info Available:</strong> {debugInfo ? 'Yes' : 'No'}
                  <br />
                  <strong>Filters Applied:</strong> {Object.values(filters).some(f => f !== '') ? 'Yes' : 'No'}
                  <br />
                  <strong>Show Debug Panel:</strong> {showDebug ? 'True' : 'False'}
                  <br />
                  <strong>Environment:</strong> {typeof window !== 'undefined' ? 'Client' : 'Server'}
                </div>
              </div>
            </div>

            {debugInfo && (
              <div className="bg-white p-4 rounded border">
                <h4 className="font-semibold text-gray-800 mb-2">📡 API RESPONSE ANALYSIS:</h4>
                <div className="space-y-2">
                  <div className="p-2 bg-gray-50 rounded">
                    <strong>Response Structure:</strong>
                    <pre className="text-xs mt-1 overflow-auto">
{JSON.stringify(debugInfo.responseStructure, null, 2)}
                    </pre>
                  </div>
                  <div className="p-2 bg-gray-50 rounded">
                    <strong>Search Criteria Used:</strong>
                    <pre className="text-xs mt-1 overflow-auto">
{JSON.stringify(debugInfo.searchCriteria, null, 2)}
                    </pre>
                  </div>
                  <div className="p-2 bg-gray-50 rounded">
                    <strong>Full API Response:</strong>
                    <pre className="text-xs mt-1 overflow-auto max-h-40">
{JSON.stringify(debugInfo.apiResponse, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-white p-4 rounded border">
              <h4 className="font-semibold text-gray-800 mb-2">✅ TROUBLESHOOTING CHECKLIST:</h4>
              <div className="space-y-2">
                <div className={`p-2 rounded text-sm ${jobs.length > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  Jobs Available for Display: {jobs.length > 0 ? `✅ ${jobs.length} jobs found` : '❌ No jobs in state'}
                </div>
                <div className={`p-2 rounded text-sm ${!loading ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  Loading State: {!loading ? '✅ Not loading (ready to display)' : '⏳ Currently loading'}
                </div>
                <div className={`p-2 rounded text-sm ${!error ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  Error State: {!error ? '✅ No errors detected' : `❌ Error: ${error}`}
                </div>
                <div className={`p-2 rounded text-sm ${debugInfo?.apiResponse ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  API Response: {debugInfo?.apiResponse ? '✅ API responded' : '❌ No API response received'}
                </div>
                <div className={`p-2 rounded text-sm ${hasSearched ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  Search Performed: {hasSearched ? '✅ Search was executed' : '⏳ No search performed yet'}
                </div>
              </div>
            </div>

            {jobs.length > 0 && (
              <div className="bg-white p-4 rounded border">
                <h4 className="font-semibold text-gray-800 mb-2">🎯 JOBS READY FOR DISPLAY:</h4>
                <div className="space-y-1 text-xs">
                  {jobs.slice(0, 3).map((job: any, index: number) => (
                    <div key={index} className="p-2 bg-gray-50 rounded">
                      <strong>Job {index + 1}:</strong> {job.job_title || job.title} at {job.company_name} ({job.location})
                    </div>
                  ))}
                  {jobs.length > 3 && (
                    <div className="p-2 bg-gray-100 rounded text-center">
                      ... and {jobs.length - 3} more jobs
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Searching for jobs...</p>
          <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
        </div>
      )}

      {/* Results Display */}
      {jobs.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Found {jobs.length} {jobs.length === 1 ? 'job' : 'jobs'}
            </h3>
            <span className="text-sm text-gray-500">
              Sorted by relevance
            </span>
          </div>

          <div className="grid gap-4">
            {jobs.map((job, index) => (
              <div
                key={job.job_id || index}
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-900 mb-1">
                        {job.job_title}
                      </h4>
                      <p className="text-blue-600 font-medium mb-2">
                        {job.company_name}
                      </p>
                    </div>
                    {job.relevance_score && (
                      <div className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                        {job.relevance_score}% match
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {job.location}
                    </div>
                    {job.experience_level && (
                      <div className="flex items-center gap-1">
                        <Briefcase className="h-4 w-4" />
                        {job.experience_level}
                      </div>
                    )}
                    {job.date_first_seen && (
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(job.date_first_seen)}
                      </div>
                    )}
                    {job.remote_friendly && (
                      <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                        Remote Friendly
                      </span>
                    )}
                  </div>

                  {job.salary_range && (
                    <div className="text-sm text-gray-700 mb-3">
                      <strong>Salary:</strong> {job.salary_range}
                    </div>
                  )}

                  {job.description && (
                    <p className="text-gray-700 text-sm mb-4 line-clamp-2">
                      {job.description}
                    </p>
                  )}

                  {job.key_skills && job.key_skills.length > 0 && (
                    <div className="mb-4">
                      <div className="flex flex-wrap gap-1">
                        {job.key_skills.slice(0, 5).map((skill, idx) => (
                          <span
                            key={idx}
                            className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                          >
                            {skill}
                          </span>
                        ))}
                        {job.key_skills.length > 5 && (
                          <span className="text-gray-500 text-xs px-2 py-1">
                            +{job.key_skills.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {job.reasoning && (
                    <div className="text-xs text-gray-600 mb-4 bg-gray-50 p-2 rounded">
                      <strong>Why this matches:</strong> {job.reasoning}
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      {job.department && `${job.department} • `}
                      Posted {formatDate(job.date_first_seen || new Date().toISOString())}
                    </div>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Apply Now
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
