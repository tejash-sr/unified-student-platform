'use client'

import React from 'react'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import apiClient from '@/services/api'
import { BarChart3, TrendingUp, BookOpen, DollarSign, AlertCircle, Sparkles } from 'lucide-react'

export default function DashboardPage() {
  const { user } = useAuth()
  const [strategy, setStrategy] = React.useState<any>(null)
  const [recommendations, setRecommendations] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const loadData = async () => {
      try {
        const [strategyData, recsData] = await Promise.all([
          apiClient.analyzeUser(),
          apiClient.getRecommendations(),
        ])
        setStrategy(strategyData.strategy)
        setRecommendations(recsData)
      } catch (error) {
        console.error('Error loading dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    if (user) loadData()
  }, [user])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="md:ml-64 p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">
          Welcome back, {user?.first_name}! 👋
        </h1>
        <p className="text-neutral-600">Here's your personalized education journey</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { icon: BarChart3, label: 'Engagement Score', value: recommendations?.engagement_score || '0', color: 'primary' },
          { icon: BookOpen, label: 'Saved Courses', value: '12', color: 'blue' },
          { icon: DollarSign, label: 'Loan Eligibility', value: '₹' + (recommendations?.loan_eligibility || '0') + 'L', color: 'green' },
          { icon: TrendingUp, label: 'Avg ROI', value: recommendations?.avg_roi + '%' || '0%', color: 'purple' },
        ].map((stat, idx) => {
          const Icon = stat.icon
          return (
            <div key={idx} className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-neutral-600 text-sm font-medium">{stat.label}</p>
                  <p className="text-2xl font-bold text-neutral-900 mt-1">{stat.value}</p>
                </div>
                <Icon size={32} className={`text-${stat.color}-600`} />
              </div>
            </div>
          )
        })}
      </div>

      {/* AI Growth Strategy */}
      {strategy && (
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-8 mb-8 border border-primary-200">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="text-primary-600" size={28} />
            <h2 className="text-2xl font-bold text-neutral-900">Your AI-Powered Growth Strategy</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Lead Intelligence */}
            <div className="bg-white p-6 rounded-lg">
              <h3 className="font-bold text-neutral-900 mb-3">📊 Lead Assessment</h3>
              <p className="text-sm text-neutral-700 mb-2">
                <strong>Tier:</strong> <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded font-medium text-xs">{strategy.lead_intelligence?.lead_tier}</span>
              </p>
              <p className="text-sm text-neutral-700 mb-2">
                <strong>Score:</strong> {strategy.lead_intelligence?.lead_score}/100
              </p>
              <div className="space-y-1">
                {strategy.lead_intelligence?.key_signals?.slice(0, 2).map((signal: string, idx: number) => (
                  <p key={idx} className="text-sm text-neutral-600">✓ {signal}</p>
                ))}
              </div>
            </div>

            {/* Next Steps */}
            <div className="bg-white p-6 rounded-lg">
              <h3 className="font-bold text-neutral-900 mb-3">🎯 Next Actions</h3>
              <div className="space-y-2">
                {strategy.engagement_plan?.action_sequence?.slice(0, 3).map((action: any, idx: number) => (
                  <p key={idx} className="text-sm text-neutral-700">
                    {idx + 1}. {action.type === 'send_email' ? '📧' : action.type === 'trigger_chatbot' ? '🤖' : '📱'} {action.description}
                  </p>
                ))}
              </div>
            </div>
          </div>

          {/* Conversion Plan */}
          {strategy.conversion_plan?.offers && (
            <div className="mt-6">
              <h3 className="font-bold text-neutral-900 mb-3">💰 Recommended Loan Offers</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {strategy.conversion_plan.offers.map((offer: any, idx: number) => (
                  <Link
                    key={idx}
                    href="/dashboard/loans"
                    className="bg-white p-4 rounded-lg border border-primary-300 hover:shadow-md transition cursor-pointer"
                  >
                    <h4 className="font-semibold text-neutral-900">{offer.name}</h4>
                    <p className="text-sm text-neutral-600 mt-1">
                      ₹{offer.amount_range[0] / 100000}L - ₹{offer.amount_range[1] / 100000}L
                    </p>
                    <p className="text-sm text-neutral-600">Rate: {offer.interest_rate}%/year</p>
                    <p className="text-xs text-success mt-2">✓ {offer.approval_probability} approval chance</p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommended Courses */}
      {recommendations?.recommended_courses && (
        <div className="bg-white rounded-lg p-8 border border-neutral-200 shadow-sm mb-8">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">🎓 Courses Recommended For You</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recommendations.recommended_courses.slice(0, 3).map((course: any, idx: number) => (
              <Link
                key={idx}
                href={`/dashboard/courses/${course.id}`}
                className="p-4 border border-neutral-200 rounded-lg hover:shadow-md transition"
              >
                <h3 className="font-bold text-neutral-900">{course.name}</h3>
                <p className="text-sm text-neutral-600 mt-1">{course.university}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs font-semibold text-primary-600">Match: {course.match_score}%</span>
                  <span className="text-xs text-neutral-500">₹{course.total_cost / 100000}L</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Churn Warning */}
      {recommendations?.churn_risk === 'high' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex gap-4">
          <AlertCircle className="text-danger flex-shrink-0" size={24} />
          <div>
            <h3 className="font-bold text-danger mb-1">We want to help you succeed!</h3>
            <p className="text-sm text-danger">Based on your profile, our team recommends scheduling a 1-on-1 consultation. Let's discuss your goals and find the perfect course + loan combination.</p>
            <button className="mt-3 text-sm font-semibold text-danger underline hover:no-underline">
              Schedule Free Consultation →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
