'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useForm } from 'react-hook-form'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface SignupFormData {
  email: string
  password: string
  confirmPassword: string
  first_name: string
  last_name: string
  current_degree: string
  current_cgpa: number
  work_experience_years: number
  annual_income: number
  preferred_countries: string[]
  preferred_fields: string[]
}

const COUNTRIES = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'Netherlands', 'Singapore']
const FIELDS = ['Computer Science', 'Data Science', 'Business', 'Engineering', 'Medicine', 'Finance']

export default function SignupPage() {
  const router = useRouter()
  const { signup, isLoading, error, clearError } = useAuth()
  const [step, setStep] = React.useState(1)
  const { register, handleSubmit, formState: { errors }, watch } = useForm<SignupFormData>({
    defaultValues: {
      preferred_countries: [],
      preferred_fields: [],
    },
  })

  const password = watch('password')
  const selectedCountries = watch('preferred_countries')
  const selectedFields = watch('preferred_fields')

  const onSubmit = async (data: SignupFormData) => {
    try {
      if (data.password !== data.confirmPassword) {
        alert('Passwords do not match')
        return
      }
      
      const { confirmPassword, ...submitData } = data
      await signup(submitData)
      router.push('/dashboard')
    } catch (err) {
      console.error('Signup error:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-2xl">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-xl">✓</span>
            </div>
            <h1 className="text-3xl font-bold text-neutral-900">Create Account</h1>
            <p className="text-neutral-600 mt-2">
              {step === 1 ? 'Basic Information' : step === 2 ? 'Academic Profile' : 'Preferences'}
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8 flex gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-1 flex-1 rounded-full ${s <= step ? 'bg-primary-600' : 'bg-neutral-200'}`}
              />
            ))}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Step 1: Basic Info */}
            {step === 1 && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      placeholder="John"
                      className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      {...register('first_name', { required: 'First name is required' })}
                    />
                    {errors.first_name && (
                      <p className="text-sm text-danger mt-1">{errors.first_name.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      placeholder="Doe"
                      className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      {...register('last_name', { required: 'Last name is required' })}
                    />
                    {errors.last_name && (
                      <p className="text-sm text-danger mt-1">{errors.last_name.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address',
                      },
                    })}
                  />
                  {errors.email && (
                    <p className="text-sm text-danger mt-1">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('password', {
                      required: 'Password is required',
                      minLength: { value: 8, message: 'Password must be at least 8 characters' },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                        message: 'Password must have uppercase, lowercase, and number',
                      },
                    })}
                  />
                  {errors.password && (
                    <p className="text-sm text-danger mt-1">{errors.password.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('confirmPassword', {
                      required: 'Please confirm your password',
                      validate: (value) => value === password || 'Passwords do not match',
                    })}
                  />
                  {errors.confirmPassword && (
                    <p className="text-sm text-danger mt-1">{errors.confirmPassword.message}</p>
                  )}
                </div>
              </>
            )}

            {/* Step 2: Academic */}
            {step === 2 && (
              <>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Current Degree
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('current_degree', { required: 'Degree is required' })}
                  >
                    <option value="">Select your degree</option>
                    <option value="B.Tech">B.Tech / Engineering</option>
                    <option value="BA">BA / Liberal Arts</option>
                    <option value="B.Sc">B.Sc / Science</option>
                    <option value="BBA">BBA / Commerce</option>
                    <option value="High School">High School</option>
                  </select>
                  {errors.current_degree && (
                    <p className="text-sm text-danger mt-1">{errors.current_degree.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Current CGPA / Score
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="4"
                    placeholder="3.8"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('current_cgpa', {
                      required: 'CGPA is required',
                      min: { value: 0, message: 'CGPA must be positive' },
                      max: { value: 4, message: 'CGPA must be 4.0 or less' },
                    })}
                  />
                  {errors.current_cgpa && (
                    <p className="text-sm text-danger mt-1">{errors.current_cgpa.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Work Experience (Years)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    placeholder="0"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('work_experience_years', {
                      required: 'Work experience is required',
                      min: { value: 0, message: 'Must be 0 or more' },
                    })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Annual Income (₹)
                  </label>
                  <input
                    type="number"
                    placeholder="800000"
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    {...register('annual_income', { required: 'Income is required' })}
                  />
                  {errors.annual_income && (
                    <p className="text-sm text-danger mt-1">{errors.annual_income.message}</p>
                  )}
                </div>
              </>
            )}

            {/* Step 3: Preferences */}
            {step === 3 && (
              <>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-3">
                    Preferred Countries (Select at least 1)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {COUNTRIES.map((country) => (
                      <label key={country} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          value={country}
                          className="w-4 h-4"
                          {...register('preferred_countries')}
                        />
                        <span className="text-neutral-700">{country}</span>
                      </label>
                    ))}
                  </div>
                  {selectedCountries.length === 0 && (
                    <p className="text-sm text-danger mt-2">Please select at least one country</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-3">
                    Preferred Fields (Select at least 1)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {FIELDS.map((field) => (
                      <label key={field} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          value={field}
                          className="w-4 h-4"
                          {...register('preferred_fields')}
                        />
                        <span className="text-neutral-700">{field}</span>
                      </label>
                    ))}
                  </div>
                  {selectedFields.length === 0 && (
                    <p className="text-sm text-danger mt-2">Please select at least one field</p>
                  )}
                </div>
              </>
            )}

            {/* Buttons */}
            <div className="flex gap-4 mt-8">
              <button
                type="button"
                onClick={() => setStep(Math.max(1, step - 1))}
                disabled={step === 1}
                className="flex-1 border border-neutral-300 text-neutral-700 py-2 rounded-lg hover:bg-neutral-50 transition font-medium disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <ChevronLeft size={20} /> Back
              </button>
              {step < 3 ? (
                <button
                  type="button"
                  onClick={() => setStep(Math.min(3, step + 1))}
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition font-medium flex items-center justify-center gap-2"
                >
                  Next <ChevronRight size={20} />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={isLoading || selectedCountries.length === 0 || selectedFields.length === 0}
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50"
                >
                  {isLoading ? 'Creating Account...' : 'Create Account'}
                </button>
              )}
            </div>
          </form>

          <div className="mt-6 text-center">
            <p className="text-neutral-600">
              Already have an account?{' '}
              <Link href="/login" className="text-primary-600 font-semibold hover:underline">
                Login here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
