'use client'

import { useState } from 'react'

export default function OpenAITestPage() {
  const [apiKey, setApiKey] = useState('')
  const [testResult, setTestResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [jobSearchResult, setJobSearchResult] = useState<any>(null)

  const testOpenAIConnection = async () => {
    if (!apiKey.trim()) {
      alert('Please enter your OpenAI API key')
      return
    }

    setLoading(true)
    setTestResult(null)

    try {
      const response = await fetch('/api/test/openai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
      })

      const data = await response.json()
      setTestResult(data)
    } catch (error) {
      setTestResult({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setLoading(false)
    }
  }

  const testJobSearch = async () => {
    if (!apiKey.trim()) {
      alert('Please enter your OpenAI API key')
      return
    }

    setLoading(true)
    setJobSearchResult(null)

    try {
      const response = await fetch('/api/backend/jobs/search-enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          companies: ['Google', 'Microsoft'],
          criteria: {
            locations: ['Remote', 'San Francisco'],
            title_keywords: ['Software Engineer'],
            experience_levels: ['senior'],
            remote_allowed: true
          }
        }),
      })

      const data = await response.json()
      setJobSearchResult(data)
    } catch (error) {
      setJobSearchResult({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">OpenAI Integration Test</h1>
        
        {/* API Key Input */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">1. Enter OpenAI API Key</h2>
          <div className="flex gap-4">
            <input
              type="password"
              value={apiKey}
              onChange={(e: any) => setApiKey(e.target.value)}
              placeholder="sk-..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={testOpenAIConnection}
              disabled={loading || !apiKey.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Testing...' : 'Test Connection'}
            </button>
          </div>
        </div>

        {/* Connection Test Results */}
        {testResult && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">2. Connection Test Results</h2>
            <div className={`p-4 rounded-md ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <pre className="text-sm overflow-auto">
                {JSON.stringify(testResult, null, 2)}
              </pre>
            </div>
            
            {testResult.success && (
              <button
                onClick={testJobSearch}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
              >
                {loading ? 'Searching...' : 'Test Job Search'}
              </button>
            )}
          </div>
        )}

        {/* Job Search Results */}
        {jobSearchResult && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">3. Job Search Test Results</h2>
            <div className={`p-4 rounded-md ${jobSearchResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <pre className="text-sm overflow-auto max-h-96">
                {JSON.stringify(jobSearchResult, null, 2)}
              </pre>
            </div>
            
            {jobSearchResult.success && jobSearchResult.jobs && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3">Found Jobs ({jobSearchResult.jobs.length})</h3>
                <div className="space-y-4">
                  {jobSearchResult.jobs.map((job: any, index: number) => (
                    <div key={index} className="border border-gray-200 rounded-md p-4">
                      <h4 className="font-semibold text-blue-600">{job.job_title}</h4>
                      <p className="text-gray-600">{job.company_name} • {job.location}</p>
                      <p className="text-sm text-gray-500 mt-1">{job.description?.substring(0, 200)}...</p>
                      <div className="mt-2 flex gap-4 text-xs text-gray-500">
                        <span>Experience: {job.experience_level}</span>
                        <span>Salary: {job.salary_range}</span>
                        <span>Method: {job.search_method}</span>
                        <span>Score: {job.relevance_score}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Instructions</h3>
          <ol className="text-blue-800 space-y-1 text-sm">
            <li>1. Enter your OpenAI API key (get one from <a href="https://platform.openai.com/api-keys" target="_blank" className="underline">OpenAI Platform</a>)</li>
            <li>2. Click "Test Connection" to verify your API key works</li>
            <li>3. If connection succeeds, click "Test Job Search" to test the full integration</li>
            <li>4. Review the results to ensure jobs are being found correctly</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
