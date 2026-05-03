'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useForm } from 'react-hook-form'

interface LoginFormData {
  email: string
  password: string
}

export default function LoginPage() {
  const router = useRouter()
  const { login, isLoading, error } = useAuth()
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>()

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.email, data.password)
      router.push('/dashboard')
    } catch (err) {
      console.error('Login error:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-xl">✓</span>
            </div>
            <h1 className="text-3xl font-bold text-neutral-900">Welcome Back</h1>
            <p className="text-neutral-600 mt-2">Login to your account</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email */}
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

            {/* Password */}
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
                  minLength: { value: 6, message: 'Password must be at least 6 characters' },
                })}
              />
              {errors.password && (
                <p className="text-sm text-danger mt-1">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50"
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-neutral-600">
              Don't have an account?{' '}
              <Link href="/signup" className="text-primary-600 font-semibold hover:underline">
                Sign up here
              </Link>
            </p>
          </div>

          <div className="mt-6 pt-6 border-t border-neutral-200">
            <p className="text-xs text-neutral-500 text-center">
              Demo credentials: demo@example.com / password123
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
