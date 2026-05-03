'use client'

import React from 'react'
import Link from 'next/link'
import { ArrowRight, BookOpen, DollarSign, Users, Zap, Shield, TrendingUp } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-neutral-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-neutral-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">✓</span>
            </div>
            <span className="font-bold text-lg">StudePath</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-neutral-700 hover:text-primary-600">
              Login
            </Link>
            <Link
              href="/signup"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-neutral-900 mb-6">
            Your Path to <span className="text-primary-600">Global Education</span>
          </h1>
          <p className="text-xl text-neutral-600 mb-8 max-w-3xl mx-auto">
            Discover the perfect course, get AI-powered guidance, and secure flexible education financing—all in one intelligent platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition flex items-center justify-center gap-2"
            >
              Get Started <ArrowRight size={20} />
            </Link>
            <Link
              href="/demo"
              className="border-2 border-primary-600 text-primary-600 px-8 py-3 rounded-lg hover:bg-primary-50 transition"
            >
              Watch Demo
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {[
            { value: '500+', label: 'Universities' },
            { value: '10K+', label: 'Courses' },
            { value: '₹100Cr+', label: 'Loans Processed' },
          ].map((stat, idx) => (
            <div key={idx} className="bg-white p-6 rounded-lg border border-neutral-200 text-center">
              <p className="text-3xl font-bold text-primary-600">{stat.value}</p>
              <p className="text-neutral-600">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-neutral-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold mb-12 text-center">Why Choose StudePath?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Zap,
                title: 'AI-Powered Matching',
                description: 'Smart algorithms match you with perfect courses based on your interests, abilities, and goals.',
              },
              {
                icon: DollarSign,
                title: 'Flexible Financing',
                description: 'Get instant eligibility checks, competitive rates, and transparent EMI calculations.',
              },
              {
                icon: BookOpen,
                title: 'Global Opportunities',
                description: 'Explore universities and programs from top institutions worldwide.',
              },
              {
                icon: Users,
                title: '24/7 AI Assistant',
                description: 'Chat with our intelligent assistant for instant guidance on courses, loans, and career paths.',
              },
              {
                icon: TrendingUp,
                title: 'ROI Tracking',
                description: 'Understand the financial impact of your education with detailed ROI projections.',
              },
              {
                icon: Shield,
                title: 'Secure & Transparent',
                description: 'Your data is protected with enterprise-grade security and privacy standards.',
              },
            ].map((feature, idx) => {
              const Icon = feature.icon
              return (
                <div key={idx} className="bg-neutral-800 p-6 rounded-lg hover:bg-neutral-700 transition">
                  <Icon size={32} className="text-primary-400 mb-4" />
                  <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                  <p className="text-neutral-400">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h2 className="text-4xl font-bold mb-6">Ready to Start Your Journey?</h2>
        <p className="text-xl text-neutral-600 mb-8">Join thousands of students making informed decisions about their future.</p>
        <Link
          href="/signup"
          className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition text-lg font-semibold"
        >
          Sign Up Now
        </Link>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-neutral-400 py-8 border-t border-neutral-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2026 StudePath. Built for the TensorFlow Competition.</p>
        </div>
      </footer>
    </div>
  )
}
