'use client'

import { useState } from 'react'
import { Search, Plus, Trash2, AlertCircle } from 'lucide-react'

interface Company {
  company_name: string
  career_page_url?: string
}

interface JobSearchProps {
  onSearch: (companies: Company[]) => Promise<any>
  loading: boolean
}

export default function JobSearch({ onSearch, loading }: JobSearchProps) {
  const [companies, setCompanies] = useState<Company[]>([
    { company_name: '', career_page_url: '' }
  ])
  const [searchResults, setSearchResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const addCompany = () => {
    setCompanies([...companies, { company_name: '', career_page_url: '' }])
  }

  const removeCompany = (index: number) => {
    if (companies.length > 1) {
      setCompanies(companies.filter((_, i) => i !== index))
    }
  }

  const updateCompany = (index: number, field: keyof Company, value: string) => {
    const updated = companies.map((company, i) => 
      i === index ? { ...company, [field]: value } : company
    )
    setCompanies(updated)
  }

  const handleSearch = async () => {
    setError(null)
    setSearchResults(null)

    // Validate companies
    const validCompanies = companies.filter(c => c.company_name.trim())
    if (validCompanies.length === 0) {
      setError('Please add at least one company name')
      return
    }

    try {
      const results = await onSearch(validCompanies)
      setSearchResults(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    }
  }

  const loadPresetCompanies = () => {
    const presetCompanies = [
      { company_name: 'Google', career_page_url: 'https://careers.google.com/' },
      { company_name: 'Microsoft', career_page_url: 'https://careers.microsoft.com/' },
      { company_name: 'OpenAI', career_page_url: 'https://openai.com/careers/' },
      { company_name: 'Meta', career_page_url: 'https://www.metacareers.com/' },
      { company_name: 'Apple', career_page_url: 'https://jobs.apple.com/' }
    ]
    setCompanies(presetCompanies)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Job Search</h2>
          <p className="text-gray-600 mt-1">Search for jobs across multiple companies</p>
        </div>
        <button
          onClick={loadPresetCompanies}
          className="btn-outline mt-4 sm:mt-0"
        >
          Load Example Companies
        </button>
      </div>

      {/* Search Form */}
      <div className="card p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Companies to Search</h3>
            <button
              onClick={addCompany}
              className="btn-primary flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Company
            </button>
          </div>

          {companies.map((company, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 border border-gray-200 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={company.company_name}
                  onChange={(e) => updateCompany(index, 'company_name', e.target.value)}
                  placeholder="e.g. Google, Microsoft, OpenAI"
                  className="input w-full"
                  required
                />
              </div>
              
              <div className="flex space-x-2">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Career Page URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={company.career_page_url}
                    onChange={(e) => updateCompany(index, 'career_page_url', e.target.value)}
                    placeholder="https://careers.company.com"
                    className="input w-full"
                  />
                </div>
                
                {companies.length > 1 && (
                  <div className="flex items-end">
                    <button
                      onClick={() => removeCompany(index)}
                      className="btn-secondary p-2"
                      title="Remove company"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {error && (
            <div className="bg-danger-50 border border-danger-200 rounded-md p-4">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-danger-400" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-danger-800">Error</h3>
                  <p className="mt-1 text-sm text-danger-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end pt-4 border-t">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="btn-primary flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Search Jobs
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Search Results</h3>
          
          <div className="bg-success-50 border border-success-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <Search className="h-5 w-5 text-success-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-success-800">
                  Search Completed Successfully
                </h3>
                <p className="mt-1 text-sm text-success-700">
                  Found {searchResults.total_jobs_found} total jobs across {searchResults.results?.length || 0} companies
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {searchResults.results?.map((result: any, index: number) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{result.company_name}</h4>
                  <span className="text-sm text-gray-600">{result.jobs_found} jobs found</span>
                </div>
                
                {result.error ? (
                  <div className="text-sm text-danger-600">
                    Error: {result.error}
                  </div>
                ) : result.summary ? (
                  <div className="text-sm text-gray-600">
                    <span className="text-success-600 font-medium">{result.summary.new_jobs}</span> new jobs, {' '}
                    <span className="text-warning-600 font-medium">{result.summary.updated_jobs}</span> updated, {' '}
                    <span className="text-gray-600 font-medium">{result.summary.unchanged_jobs}</span> unchanged
                  </div>
                ) : null}
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t text-center">
            <p className="text-sm text-gray-600">
              Results have been saved to the database. Visit the{' '}
              <span className="font-medium">Jobs</span> tab to view all discovered opportunities.
            </p>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">How it works</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Enter company names you're interested in</li>
          <li>• Optionally provide career page URLs for more targeted searches</li>
          <li>• The system will use AI to search for relevant job opportunities</li>
          <li>• New jobs are automatically tracked and status changes are monitored</li>
          <li>• You can export results or set up automated daily monitoring</li>
        </ul>
      </div>
    </div>
  )
}
