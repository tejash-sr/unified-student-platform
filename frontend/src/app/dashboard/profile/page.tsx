'use client'

import React from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useForm } from 'react-hook-form'
import apiClient from '@/services/api'
import { Save } from 'lucide-react'

export default function ProfilePage() {
  const { user, updateProfile, isLoading } = useAuth()
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: user,
  })

  React.useEffect(() => {
    if (user) {
      reset(user)
    }
  }, [user, reset])

  const onSubmit = async (data: any) => {
    try {
      await updateProfile(data)
      alert('Profile updated successfully!')
    } catch (error) {
      console.error('Update error:', error)
      alert('Failed to update profile')
    }
  }

  if (!user) return <div>Loading...</div>

  return (
    <div className="md:ml-64 p-6 max-w-4xl">
      <h1 className="text-3xl font-bold text-neutral-900 mb-8">👤 My Profile</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg p-8 border border-neutral-200">
        {/* Personal Info */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">First Name</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('first_name')}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Last Name</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('last_name')}
              />
            </div>
          </div>
        </div>

        {/* Academic Info */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Academic Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Current Degree</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('current_degree')}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">CGPA</label>
              <input
                type="number"
                step="0.1"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('current_cgpa', { valueAsNumber: true })}
              />
            </div>
          </div>
        </div>

        {/* Professional Info */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Professional Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Work Experience (Years)</label>
              <input
                type="number"
                step="0.5"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('work_experience_years', { valueAsNumber: true })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Annual Income (₹)</label>
              <input
                type="number"
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                {...register('annual_income', { valueAsNumber: true })}
              />
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Preferences</h2>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-3">Preferred Countries</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {['USA', 'UK', 'Canada', 'Australia', 'Germany', 'Netherlands'].map((country) => (
                <label key={country} className="flex items-center gap-2">
                  <input type="checkbox" defaultChecked={user?.preferred_countries?.includes(country)} className="w-4 h-4" />
                  <span className="text-neutral-700">{country}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isLoading}
            className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50"
          >
            <Save size={20} /> Save Changes
          </button>
        </div>
      </form>
    </div>
  )
}
