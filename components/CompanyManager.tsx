'use client'

import { useState, useEffect } from 'react'
import { Building, Plus, Edit, Trash2, Save, X } from 'lucide-react'

interface Company {
  company_name: string
  career_page_url?: string
}

export default function CompanyManager() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(false)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newCompany, setNewCompany] = useState<Company>({ company_name: '', career_page_url: '' })

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/backend/companies')
      if (!response.ok) throw new Error('Failed to load companies')
      const data = await response.json()
      
      // Convert company names to company objects
      const companyObjects = data.companies.map((name: string) => ({
        company_name: name,
        career_page_url: ''
      }))
      setCompanies(companyObjects)
    } catch (err) {
      console.error('Failed to load companies:', err)
      // Set some example companies if loading fails
      setCompanies([
        { company_name: 'Google', career_page_url: 'https://careers.google.com/' },
        { company_name: 'Microsoft', career_page_url: 'https://careers.microsoft.com/' },
        { company_name: 'OpenAI', career_page_url: 'https://openai.com/careers/' }
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleAddCompany = async () => {
    if (!newCompany.company_name.trim()) return

    try {
      const response = await fetch('/api/backend/companies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newCompany),
      })

      if (!response.ok) throw new Error('Failed to add company')

      setCompanies([...companies, newCompany])
      setNewCompany({ company_name: '', career_page_url: '' })
      setShowAddForm(false)
    } catch (err) {
      console.error('Failed to add company:', err)
      // Add locally even if API fails
      setCompanies([...companies, newCompany])
      setNewCompany({ company_name: '', career_page_url: '' })
      setShowAddForm(false)
    }
  }

  const handleDeleteCompany = (index: number) => {
    if (confirm('Are you sure you want to remove this company?')) {
      setCompanies(companies.filter((_, i) => i !== index))
    }
  }

  const handleEditCompany = (index: number, updatedCompany: Company) => {
    const updated = companies.map((company, i) => 
      i === index ? updatedCompany : company
    )
    setCompanies(updated)
    setEditingIndex(null)
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-500">Loading companies...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Company Management</h2>
          <p className="text-gray-600 mt-1">Manage the companies you want to monitor for job opportunities</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary flex items-center mt-4 sm:mt-0"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Company
        </button>
      </div>

      {/* Add Company Form */}
      {showAddForm && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Company</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Name *
              </label>
              <input
                type="text"
                value={newCompany.company_name}
                onChange={(e) => setNewCompany({ ...newCompany, company_name: e.target.value })}
                placeholder="e.g. Google, Microsoft, OpenAI"
                className="input w-full"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Career Page URL (Optional)
              </label>
              <input
                type="url"
                value={newCompany.career_page_url}
                onChange={(e) => setNewCompany({ ...newCompany, career_page_url: e.target.value })}
                placeholder="https://careers.company.com"
                className="input w-full"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 mt-4">
            <button
              onClick={() => {
                setShowAddForm(false)
                setNewCompany({ company_name: '', career_page_url: '' })
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleAddCompany}
              disabled={!newCompany.company_name.trim()}
              className="btn-primary"
            >
              Add Company
            </button>
          </div>
        </div>
      )}

      {/* Companies List */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Monitored Companies ({companies.length})
          </h3>
        </div>
        
        {companies.length === 0 ? (
          <div className="p-12 text-center">
            <Building className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No companies added yet</h3>
            <p className="text-gray-500 mb-4">
              Add companies you're interested in to start monitoring their job opportunities
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary"
            >
              Add Your First Company
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {companies.map((company, index) => (
              <CompanyItem
                key={index}
                company={company}
                index={index}
                isEditing={editingIndex === index}
                onEdit={() => setEditingIndex(index)}
                onSave={(updatedCompany) => handleEditCompany(index, updatedCompany)}
                onCancel={() => setEditingIndex(null)}
                onDelete={() => handleDeleteCompany(index)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Tips for Better Results</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Use the exact company name as it appears on their website</li>
          <li>• Adding career page URLs helps the AI find more relevant jobs</li>
          <li>• You can edit company details anytime by clicking the edit button</li>
          <li>• Companies are automatically monitored when you run job searches</li>
        </ul>
      </div>
    </div>
  )
}

interface CompanyItemProps {
  company: Company
  index: number
  isEditing: boolean
  onEdit: () => void
  onSave: (company: Company) => void
  onCancel: () => void
  onDelete: () => void
}

function CompanyItem({ company, index, isEditing, onEdit, onSave, onCancel, onDelete }: CompanyItemProps) {
  const [editedCompany, setEditedCompany] = useState(company)

  useEffect(() => {
    setEditedCompany(company)
  }, [company, isEditing])

  const handleSave = () => {
    if (editedCompany.company_name.trim()) {
      onSave(editedCompany)
    }
  }

  if (isEditing) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name *
            </label>
            <input
              type="text"
              value={editedCompany.company_name}
              onChange={(e) => setEditedCompany({ ...editedCompany, company_name: e.target.value })}
              className="input w-full"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Career Page URL
            </label>
            <input
              type="url"
              value={editedCompany.career_page_url || ''}
              onChange={(e) => setEditedCompany({ ...editedCompany, career_page_url: e.target.value })}
              className="input w-full"
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-3 mt-4">
          <button onClick={onCancel} className="btn-secondary flex items-center">
            <X className="h-4 w-4 mr-2" />
            Cancel
          </button>
          <button onClick={handleSave} className="btn-primary flex items-center">
            <Save className="h-4 w-4 mr-2" />
            Save
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 flex items-center justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-3">
          <Building className="h-5 w-5 text-gray-400" />
          <div>
            <h4 className="font-medium text-gray-900">{company.company_name}</h4>
            {company.career_page_url && (
              <a
                href={company.career_page_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                {company.career_page_url}
              </a>
            )}
          </div>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={onEdit}
          className="btn-secondary flex items-center"
        >
          <Edit className="h-4 w-4 mr-2" />
          Edit
        </button>
        <button
          onClick={onDelete}
          className="btn-secondary text-danger-600 hover:text-danger-700 flex items-center"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete
        </button>
      </div>
    </div>
  )
}
