'use client'

import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useForm } from 'react-hook-form'
import apiClient from '@/services/api'

interface ROIFormData {
  total_cost: number
  loan_amount: number
  interest_rate: number
}

export default function ROICalculatorPage() {
  const [roiResult, setRoiResult] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(false)
  const { register, handleSubmit, watch } = useForm<ROIFormData>({
    defaultValues: {
      total_cost: 5000000,
      loan_amount: 3000000,
      interest_rate: 8.5,
    },
  })

  const totalCost = watch('total_cost')
  const loanAmount = watch('loan_amount')
  const interestRate = watch('interest_rate')

  const onSubmit = async (data: ROIFormData) => {
    try {
      setLoading(true)
      const result = await apiClient.calculateROI(data.total_cost, data.loan_amount, data.interest_rate)
      setRoiResult(result)
    } catch (error) {
      console.error('ROI calculation error:', error)
    } finally {
      setLoading(false)
    }
  }

  // Generate sample projection data
  const projectionData = Array.from({ length: 16 }, (_, i) => {
    const year = i
    // Assuming salary grows 5% annually, starting from 40L
    const salary = 4000000 * Math.pow(1.05, year)
    // Cumulative cost = tuition + 5 years of living expenses (estimated)
    const cumulativeCost = totalCost + year * 500000
    // Cumulative earnings
    const cumulativeEarnings = salary * year
    // Net benefit
    const netBenefit = cumulativeEarnings - (cumulativeCost + loanAmount)

    return {
      year,
      salary: Math.round(salary / 100000),
      cumulativeBenefit: Math.round(netBenefit / 1000000),
      breakeven: netBenefit >= 0,
    }
  })

  return (
    <div className="md:ml-64 p-6 max-w-7xl">
      <h1 className="text-3xl font-bold text-neutral-900 mb-8">📈 ROI Calculator</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Form */}
        <div className="lg:col-span-1">
          <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg p-6 border border-neutral-200 space-y-6 sticky top-24">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Total Course Cost (₹)
              </label>
              <input
                type="number"
                placeholder="5000000"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('total_cost', { required: true })}
              />
              <p className="text-xs text-neutral-500 mt-1">₹{(totalCost / 1000000).toFixed(1)}M</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Loan Amount (₹)
              </label>
              <input
                type="number"
                placeholder="3000000"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('loan_amount', { required: true })}
              />
              <p className="text-xs text-neutral-500 mt-1">₹{(loanAmount / 1000000).toFixed(1)}M (Own contribution: ₹{((totalCost - loanAmount) / 1000000).toFixed(1)}M)</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Interest Rate (%)
              </label>
              <input
                type="number"
                step="0.1"
                placeholder="8.5"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('interest_rate', { required: true })}
              />
              <input
                type="range"
                min="0"
                max="15"
                step="0.1"
                className="w-full mt-2"
                {...register('interest_rate')}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate ROI'}
            </button>
          </form>
        </div>

        {/* Results and Chart */}
        <div className="lg:col-span-2">
          {roiResult ? (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-300 rounded-lg p-6">
                  <p className="text-neutral-600 text-sm font-medium">5-Year Net Benefit</p>
                  <p className="text-3xl font-bold text-green-600">₹{(roiResult.net_benefit_5yr / 1000000).toFixed(1)}M</p>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-300 rounded-lg p-6">
                  <p className="text-neutral-600 text-sm font-medium">ROI (5 years)</p>
                  <p className="text-3xl font-bold text-blue-600">{roiResult.roi_percent_5yr?.toFixed(1)}%</p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-300 rounded-lg p-6">
                  <p className="text-neutral-600 text-sm font-medium">Breakeven Point</p>
                  <p className="text-3xl font-bold text-purple-600">{roiResult.breakeven_months && (roiResult.breakeven_months / 12).toFixed(1)} years</p>
                </div>
              </div>

              {/* Chart */}
              <div className="bg-white rounded-lg p-6 border border-neutral-200">
                <h3 className="font-bold text-neutral-900 mb-4">15-Year Projection</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={projectionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" label={{ value: 'Years', position: 'insideBottomRight', offset: -5 }} />
                    <YAxis label={{ value: 'Cumulative Benefit (₹M)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip
                      formatter={(value: any) => `₹${value}M`}
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="cumulativeBenefit"
                      stroke="#0ea5e9"
                      strokeWidth={2}
                      name="Cumulative Benefit"
                      dot={{ fill: '#0ea5e9', r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Details */}
              <div className="bg-white rounded-lg p-6 border border-neutral-200">
                <h3 className="font-bold text-neutral-900 mb-4">Key Assumptions</h3>
                <ul className="space-y-2 text-sm text-neutral-700">
                  <li>✓ Starting salary: ₹40L/year (post-graduation)</li>
                  <li>✓ Annual salary growth: 5%</li>
                  <li>✓ 70% of salary is available for loan repayment</li>
                  <li>✓ Loan tenure: 15 years (180 months)</li>
                  <li>✓ Living expenses during studies: ₹5L/year</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="bg-neutral-50 rounded-lg p-12 border border-neutral-200 text-center">
              <p className="text-neutral-600">Fill in the form and calculate your ROI projection</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
