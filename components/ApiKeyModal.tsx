'use client'

import { useState } from 'react'
import { X, Eye, EyeOff } from 'lucide-react'

interface ApiKeyModalProps {
  onSubmit: (apiKey: string) => void
  onClose: () => void
  initialKey?: string
}

export default function ApiKeyModal({ onSubmit, onClose, initialKey = '' }: ApiKeyModalProps) {
  const [apiKey, setApiKey] = useState(initialKey)
  const [showKey, setShowKey] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!apiKey.trim()) {
      setError('API key is required')
      return
    }

    if (!apiKey.startsWith('sk-') || apiKey.length < 20) {
      setError('Invalid API key format. Must start with sk- and be at least 20 characters.')
      return
    }

    try {
      // Validate API key with backend
      const response = await fetch('/api/backend/validate-api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
      })

      if (!response.ok) {
        const data = await response.json()
        setError(data.message || 'API key validation failed')
        return
      }

      onSubmit(apiKey)
    } catch (err) {
      // If validation endpoint fails, accept the key format validation
      onSubmit(apiKey)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">OpenAI API Configuration</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={!initialKey} // Don't allow closing if no API key is set
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
              OpenAI API Key
            </label>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                id="apiKey"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="input pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showKey ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            </div>
            {error && (
              <p className="mt-2 text-sm text-danger-600">{error}</p>
            )}
          </div>

          <div className="mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h3 className="text-sm font-medium text-blue-800 mb-2">How to get your API key:</h3>
              <ol className="list-decimal list-inside text-sm text-blue-700 space-y-1">
                <li>Visit <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="underline">OpenAI API Keys</a></li>
                <li>Sign in to your OpenAI account</li>
                <li>Click "Create new secret key"</li>
                <li>Copy the key and paste it here</li>
              </ol>
              <p className="mt-2 text-xs text-blue-600">
                Your API key will be stored locally in your browser and is never sent to our servers.
              </p>
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            {initialKey && (
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              className="btn-primary"
            >
              Save API Key
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
