'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import apiClient from '@/services/api'
import { TrendingUp, DollarSign, Calendar } from 'lucide-react'

interface EMIFormData {
  principal_amount: number
  interest_rate_annual: number
  tenure_months: number
}

export default function LoansPage() {
  const [emiResult, setEmiResult] = React.useState<any>(null)
  const [eligibilityResult, setEligibilityResult] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(false)
  const [tab, setTab] = React.useState('calculator')
  const { register, handleSubmit, watch } = useForm<EMIFormData>({
    defaultValues: {
      principal_amount: 1000000,
      interest_rate_annual: 8.5,
      tenure_months: 180,
    },
  })

  const principal = watch('principal_amount')
  const rate = watch('interest_rate_annual')
  const months = watch('tenure_months')

  const onCalculateEMI = async (data: EMIFormData) => {
    try {
      setLoading(true)
      const result = await apiClient.calculateEMI(
        data.principal_amount,
        data.interest_rate_annual,
        data.tenure_months
      )
      setEmiResult(result)
    } catch (error) {
      console.error('EMI calculation error:', error)
    } finally {
      setLoading(false)
    }
  }

  const onCheckEligibility = async () => {
    try {
      setLoading(true)
      const result = await apiClient.checkLoanEligibility(principal)
      setEligibilityResult(result)
    } catch (error) {
      console.error('Eligibility check error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="md:ml-64 p-6 max-w-7xl">
      <h1 className="text-3xl font-bold text-neutral-900 mb-8">💰 Loan Management</h1>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 border-b border-neutral-200">
        <button
          onClick={() => setTab('calculator')}
          className={`px-6 py-3 font-medium transition border-b-2 ${
            tab === 'calculator'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-neutral-600 hover:text-neutral-900'
          }`}
        >
          EMI Calculator
        </button>
        <button
          onClick={() => setTab('eligibility')}
          className={`px-6 py-3 font-medium transition border-b-2 ${
            tab === 'eligibility'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-neutral-600 hover:text-neutral-900'
          }`}
        >
          Eligibility Check
        </button>
        <button
          onClick={() => setTab('applications')}
          className={`px-6 py-3 font-medium transition border-b-2 ${
            tab === 'applications'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-neutral-600 hover:text-neutral-900'
          }`}
        >
          My Applications
        </button>
      </div>

      {/* EMI Calculator */}
      {tab === 'calculator' && (
        <div className="bg-white rounded-lg p-8 border border-neutral-200 mb-8">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">EMI Calculator</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Form */}
            <form onSubmit={handleSubmit(onCalculateEMI)} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Loan Amount (₹)
                </label>
                <input
                  type="number"
                  placeholder="1000000"
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('principal_amount', { required: true })}
                />
                <p className="text-xs text-neutral-500 mt-1">₹{(principal / 100000).toFixed(1)}L</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Interest Rate (% per annum)
                </label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="8.5"
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('interest_rate_annual', { required: true })}
                />
                <input
                  type="range"
                  min="0"
                  max="15"
                  step="0.1"
                  className="w-full mt-2"
                  {...register('interest_rate_annual')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Tenure (Months)
                </label>
                <input
                  type="number"
                  placeholder="180"
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('tenure_months', { required: true })}
                />
                <p className="text-xs text-neutral-500 mt-1">{(months / 12).toFixed(1)} years</p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate EMI'}
              </button>
            </form>

            {/* Results */}
            {emiResult && (
              <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-8 border border-primary-200">
                <h3 className="text-xl font-bold text-neutral-900 mb-6">Your EMI Details</h3>

                <div className="space-y-4">
                  <div className="bg-white p-4 rounded-lg">
                    <p className="text-neutral-600 text-sm">Monthly EMI</p>
                    <p className="text-3xl font-bold text-primary-600">₹{(emiResult.monthly_emi || 0).toLocaleString()}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-neutral-600 text-xs">Total Amount</p>
                      <p className="text-lg font-bold text-neutral-900">₹{(emiResult.total_amount || 0).toLocaleString()}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-neutral-600 text-xs">Total Interest</p>
                      <p className="text-lg font-bold text-danger">₹{(emiResult.total_interest || 0).toLocaleString()}</p>
                    </div>
                  </div>

                  <button className="w-full mt-4 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition font-medium">
                    Apply for Loan
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Eligibility Check */}
      {tab === 'eligibility' && (
        <div className="bg-white rounded-lg p-8 border border-neutral-200 mb-8">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">Check Loan Eligibility</h2>

          <div className="max-w-md mb-8">
            <label className="block text-sm font-medium text-neutral-700 mb-4">
              Requested Loan Amount (₹)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="1500000"
                defaultValue={1500000}
                className="flex-1 px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                id="eligibility-amount"
              />
              <button
                onClick={() => {
                  const amount = (document.getElementById('eligibility-amount') as HTMLInputElement).value
                  onCheckEligibility()
                }}
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50"
              >
                {loading ? 'Checking...' : 'Check'}
              </button>
            </div>
          </div>

          {eligibilityResult && (
            <div className={`rounded-lg p-8 border-2 ${
              eligibilityResult.eligibility_category === 'approved'
                ? 'bg-green-50 border-green-300'
                : eligibilityResult.eligibility_category === 'conditional'
                ? 'bg-yellow-50 border-yellow-300'
                : 'bg-red-50 border-red-300'
            }`}>
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <span>{eligibilityResult.eligibility_category === 'approved' ? '✓' : '⚠'}</span>
                {eligibilityResult.eligibility_category.toUpperCase()}
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-neutral-700 text-sm font-medium mb-2">Eligibility Score</p>
                  <div className="flex items-end gap-2">
                    <p className="text-4xl font-bold">{eligibilityResult.eligibility_score}</p>
                    <p className="text-neutral-600 pb-1">/ 100</p>
                  </div>
                </div>

                <div>
                  <p className="text-neutral-700 text-sm font-medium mb-2">Potential Loan Amount</p>
                  <p className="text-4xl font-bold">₹{(eligibilityResult.potential_approved_amount / 100000).toFixed(0)}L</p>
                </div>
              </div>

              <div className="mt-6">
                <p className="text-neutral-700 text-sm font-medium mb-3">Key Factors</p>
                <ul className="space-y-2">
                  {eligibilityResult.eligibility_reasons?.map((reason: string, idx: number) => (
                    <li key={idx} className="text-sm text-neutral-700">
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {eligibilityResult.potential_monthly_emi && (
                <div className="mt-6 p-4 bg-white rounded-lg border border-neutral-200">
                  <p className="text-neutral-600 text-sm">Est. Monthly EMI</p>
                  <p className="text-2xl font-bold text-primary-600">₹{eligibilityResult.potential_monthly_emi.toLocaleString()}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Applications */}
      {tab === 'applications' && (
        <div className="bg-white rounded-lg p-8 border border-neutral-200">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">My Loan Applications</h2>
          <p className="text-neutral-600">No active applications. Start by checking your eligibility above.</p>
        </div>
      )}
    </div>
  )
}
