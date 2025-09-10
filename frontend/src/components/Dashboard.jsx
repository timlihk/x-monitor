import React, { useState, useEffect } from 'react'
import { Plus, Play, Edit2, Trash2 } from 'lucide-react'
import { termsApi, runApi } from '../services/api'
import AddTermModal from './AddTermModal'
import LoadingSpinner from './LoadingSpinner'

const Dashboard = () => {
  const [terms, setTerms] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [runningTerm, setRunningTerm] = useState(null)

  useEffect(() => {
    loadTerms()
  }, [])

  const loadTerms = async () => {
    try {
      const response = await termsApi.getAll()
      setTerms(response.data)
    } catch (error) {
      console.error('Error loading terms:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTerm = async (termData) => {
    try {
      await termsApi.create(termData)
      loadTerms()
      setShowAddModal(false)
    } catch (error) {
      console.error('Error adding term:', error)
    }
  }

  const handleToggleActive = async (term) => {
    try {
      await termsApi.update(term.id, { active: !term.active })
      loadTerms()
    } catch (error) {
      console.error('Error updating term:', error)
    }
  }

  const handleToggleFollowing = async (term) => {
    try {
      await termsApi.update(term.id, { restrict_following: !term.restrict_following })
      loadTerms()
    } catch (error) {
      console.error('Error updating term:', error)
    }
  }

  const handleDeleteTerm = async (termId) => {
    if (window.confirm('Are you sure you want to delete this term?')) {
      try {
        await termsApi.delete(termId)
        loadTerms()
      } catch (error) {
        console.error('Error deleting term:', error)
      }
    }
  }

  const handleRunNow = async (term) => {
    setRunningTerm(term.id)
    try {
      const response = await runApi.manual({
        keyword: term.keyword,
        restrict_following: term.restrict_following
      })
      alert(`Summary generated for ${term.keyword}:\n${response.data.summary}`)
    } catch (error) {
      console.error('Error running manual job:', error)
      alert('Error running manual job. Please try again.')
    } finally {
      setRunningTerm(null)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <div className="px-4 py-6">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Monitored Terms</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage keywords, hashtags, and tickers you want to monitor on X.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Term
          </button>
        </div>
      </div>

      <div className="mt-8 overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
        <table className="min-w-full divide-y divide-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Term
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Following Only
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {terms.map((term) => (
              <tr key={term.id} className={term.active ? '' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{term.keyword}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleToggleFollowing(term)}
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      term.restrict_following
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {term.restrict_following ? 'Following Only' : 'All Users'}
                  </button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleToggleActive(term)}
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      term.active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {term.active ? 'Active' : 'Inactive'}
                  </button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(term.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <button
                    onClick={() => handleRunNow(term)}
                    disabled={runningTerm === term.id}
                    className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                  >
                    {runningTerm === term.id ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </button>
                  <button
                    onClick={() => handleDeleteTerm(term.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {terms.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No monitored terms yet. Add one to get started!</p>
          </div>
        )}
      </div>

      {showAddModal && (
        <AddTermModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddTerm}
        />
      )}
    </div>
  )
}

export default Dashboard