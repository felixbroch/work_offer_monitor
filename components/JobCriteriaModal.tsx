'use client'

import { useState } from 'react'
import { X, MapPin, Briefcase, User, Plus, Trash2 } from 'lucide-react'

interface JobCriteria {
  locations: string[]
  title_keywords: string[]
  experience_levels: string[]
  salary_min?: number
  remote_allowed: boolean
  company_types?: string[]
}

interface JobCriteriaModalProps {
  onSubmit: (criteria: JobCriteria) => void
  onClose: () => void
  initialCriteria?: JobCriteria
}

const defaultCriteria: JobCriteria = {
  locations: ['Remote', 'New York', 'San Francisco'],
  title_keywords: ['Software Engineer', 'Developer', 'Data Scientist'],
  experience_levels: ['junior', 'mid-level', 'senior'],
  remote_allowed: true,
  company_types: ['Startup', 'Enterprise', 'Tech Company']
}

export default function JobCriteriaModal({ onSubmit, onClose, initialCriteria = defaultCriteria }: JobCriteriaModalProps) {
  const [criteria, setCriteria] = useState<JobCriteria>(initialCriteria)
  const [newLocation, setNewLocation] = useState('')
  const [newKeyword, setNewKeyword] = useState('')
  const [newExperience, setNewExperience] = useState('')
  const [newCompanyType, setNewCompanyType] = useState('')

  const addLocation = () => {
    if (newLocation.trim() && !criteria.locations.includes(newLocation.trim())) {
      setCriteria(prev => ({
        ...prev,
        locations: [...prev.locations, newLocation.trim()]
      }))
      setNewLocation('')
    }
  }

  const removeLocation = (location: string) => {
    setCriteria(prev => ({
      ...prev,
      locations: prev.locations.filter(l => l !== location)
    }))
  }

  const addKeyword = () => {
    if (newKeyword.trim() && !criteria.title_keywords.includes(newKeyword.trim())) {
      setCriteria(prev => ({
        ...prev,
        title_keywords: [...prev.title_keywords, newKeyword.trim()]
      }))
      setNewKeyword('')
    }
  }

  const removeKeyword = (keyword: string) => {
    setCriteria(prev => ({
      ...prev,
      title_keywords: prev.title_keywords.filter(k => k !== keyword)
    }))
  }

  const addExperience = () => {
    if (newExperience.trim() && !criteria.experience_levels.includes(newExperience.trim())) {
      setCriteria(prev => ({
        ...prev,
        experience_levels: [...prev.experience_levels, newExperience.trim()]
      }))
      setNewExperience('')
    }
  }

  const removeExperience = (experience: string) => {
    setCriteria(prev => ({
      ...prev,
      experience_levels: prev.experience_levels.filter(e => e !== experience)
    }))
  }

  const addCompanyType = () => {
    if (newCompanyType.trim() && !criteria.company_types?.includes(newCompanyType.trim())) {
      setCriteria(prev => ({
        ...prev,
        company_types: [...(prev.company_types || []), newCompanyType.trim()]
      }))
      setNewCompanyType('')
    }
  }

  const removeCompanyType = (companyType: string) => {
    setCriteria(prev => ({
      ...prev,
      company_types: prev.company_types?.filter(c => c !== companyType) || []
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (criteria.locations.length === 0) {
      alert('Please add at least one location')
      return
    }
    
    if (criteria.title_keywords.length === 0) {
      alert('Please add at least one job title keyword')
      return
    }
    
    if (criteria.experience_levels.length === 0) {
      alert('Please add at least one experience level')
      return
    }

    onSubmit(criteria)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            🎯 Configure Job Search Criteria
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Locations */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-3">
              <MapPin className="h-4 w-4 mr-2" />
              Preferred Locations
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {criteria.locations.map((location, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                >
                  {location}
                  <button
                    type="button"
                    onClick={() => removeLocation(location)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                placeholder="Add location (e.g., Remote, New York, London)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addLocation}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Job Title Keywords */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-3">
              <Briefcase className="h-4 w-4 mr-2" />
              Job Title Keywords
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {criteria.title_keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800"
                >
                  {keyword}
                  <button
                    type="button"
                    onClick={() => removeKeyword(keyword)}
                    className="ml-2 text-green-600 hover:text-green-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyword())}
                placeholder="Add job title keyword (e.g., Software Engineer, Data Scientist)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addKeyword}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Experience Levels */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-3">
              <User className="h-4 w-4 mr-2" />
              Experience Levels
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {criteria.experience_levels.map((level, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
                >
                  {level}
                  <button
                    type="button"
                    onClick={() => removeExperience(level)}
                    className="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newExperience}
                onChange={(e) => setNewExperience(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addExperience())}
                placeholder="Add experience level (e.g., junior, senior, entry-level)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addExperience}
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Salary and Preferences */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Salary (optional)
              </label>
              <input
                type="number"
                value={criteria.salary_min || ''}
                onChange={(e) => setCriteria(prev => ({
                  ...prev,
                  salary_min: e.target.value ? parseInt(e.target.value) : undefined
                }))}
                placeholder="e.g., 80000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="flex items-center">
              <label className="flex items-center text-sm font-medium text-gray-700">
                <input
                  type="checkbox"
                  checked={criteria.remote_allowed}
                  onChange={(e) => setCriteria(prev => ({
                    ...prev,
                    remote_allowed: e.target.checked
                  }))}
                  className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                Include Remote Positions
              </label>
            </div>
          </div>

          {/* Company Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Company Types (optional)
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {criteria.company_types?.map((type, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800"
                >
                  {type}
                  <button
                    type="button"
                    onClick={() => removeCompanyType(type)}
                    className="ml-2 text-orange-600 hover:text-orange-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newCompanyType}
                onChange={(e) => setNewCompanyType(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCompanyType())}
                placeholder="Add company type (e.g., Startup, Enterprise, Non-profit)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addCompanyType}
                className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Submit buttons */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Save Criteria
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
