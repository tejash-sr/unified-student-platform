'use client'

import React from 'react'
import Link from 'next/link'
import { Search, Filter, MapPin, Users, TrendingUp } from 'lucide-react'
import apiClient from '@/services/api'

export default function CoursesPage() {
  const [courses, setCourses] = React.useState<any[]>([])
  const [loading, setLoading] = React.useState(true)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [selectedField, setSelectedField] = React.useState('')
  const [selectedCountry, setSelectedCountry] = React.useState('')

  React.useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await apiClient.discoverCourses(selectedField || undefined, selectedCountry || undefined, undefined, 20)
        setCourses(data.courses || [])
      } catch (error) {
        console.error('Error loading courses:', error)
      } finally {
        setLoading(false)
      }
    }

    loadCourses()
  }, [selectedField, selectedCountry])

  const filteredCourses = courses.filter((course) =>
    course.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    course.university.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="md:ml-64 p-6 max-w-7xl">
      {/* Header */}
      <h1 className="text-3xl font-bold text-neutral-900 mb-8">🎓 Explore Courses</h1>

      {/* Search & Filters */}
      <div className="bg-white rounded-lg p-6 border border-neutral-200 mb-8">
        <div className="flex flex-col gap-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 text-neutral-400" size={20} />
              <input
                type="text"
                placeholder="Search courses or universities..."
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition flex items-center gap-2">
              <Filter size={20} /> Search
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <select
              className="px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
            >
              <option value="">All Fields</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Data Science">Data Science</option>
              <option value="Business">Business</option>
              <option value="Engineering">Engineering</option>
            </select>
            <select
              className="px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
            >
              <option value="">All Countries</option>
              <option value="USA">USA</option>
              <option value="UK">UK</option>
              <option value="Canada">Canada</option>
              <option value="Australia">Australia</option>
            </select>
          </div>
        </div>
      </div>

      {/* Courses Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.length > 0 ? (
            filteredCourses.map((course) => (
              <Link
                key={course.id}
                href={`/dashboard/courses/${course.id}`}
                className="bg-white rounded-lg border border-neutral-200 overflow-hidden hover:shadow-lg transition"
              >
                <div className="p-6">
                  <h3 className="text-lg font-bold text-neutral-900 mb-2 line-clamp-2">{course.name}</h3>
                  <p className="text-sm text-neutral-600 mb-4">{course.university}</p>

                  <div className="space-y-2 text-sm text-neutral-600 mb-4">
                    <div className="flex items-center gap-2">
                      <MapPin size={16} className="text-primary-600" />
                      {course.country}
                    </div>
                    <div className="flex items-center gap-2">
                      <Users size={16} className="text-primary-600" />
                      {course.intake_per_year} students/year
                    </div>
                  </div>

                  <div className="border-t border-neutral-200 pt-4 flex justify-between items-end">
                    <div>
                      <p className="text-xs text-neutral-500">Tuition Cost</p>
                      <p className="text-lg font-bold text-neutral-900">₹{course.total_cost / 100000}L</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-neutral-500">Est. ROI</p>
                      <p className="text-lg font-bold text-success flex items-center gap-1">
                        <TrendingUp size={16} />
                        {course.roi_percent}%
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <p className="text-neutral-600">No courses found. Try adjusting your filters.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
