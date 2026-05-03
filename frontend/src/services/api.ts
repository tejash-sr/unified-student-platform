import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

class APIClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )

    // Load token from localStorage on init
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  setToken(token: string) {
    this.token = token
    localStorage.setItem('access_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('access_token')
  }

  getToken() {
    return this.token
  }

  // ============================================================================
  // AUTH ENDPOINTS
  // ============================================================================

  async signup(data: {
    email: string
    password: string
    first_name: string
    last_name: string
    current_degree: string
    current_cgpa: number
    work_experience_years: number
    annual_income: number
    preferred_countries: string[]
    preferred_fields: string[]
  }) {
    const response = await this.client.post('/users/signup', data)
    if (response.data.access_token) {
      this.setToken(response.data.access_token)
    }
    return response.data
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/users/login', { email, password })
    if (response.data.access_token) {
      this.setToken(response.data.access_token)
    }
    return response.data
  }

  async refresh() {
    const refreshToken = localStorage.getItem('refresh_token')
    const response = await this.client.post('/users/refresh', { refresh_token: refreshToken })
    if (response.data.access_token) {
      this.setToken(response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
    }
    return response.data
  }

  async logout() {
    this.clearToken()
  }

  // ============================================================================
  // PROFILE ENDPOINTS
  // ============================================================================

  async getProfile() {
    const response = await this.client.get('/users/profile')
    return response.data
  }

  async updateProfile(data: any) {
    const response = await this.client.put('/users/profile', data)
    return response.data
  }

  async getEngagement() {
    const response = await this.client.get('/users/profile/engagement')
    return response.data
  }

  // ============================================================================
  // LOAN ENDPOINTS
  // ============================================================================

  async checkLoanEligibility(requested_amount_inr: number) {
    const response = await this.client.post('/loans/eligibility-check', {
      requested_amount_inr,
    })
    return response.data
  }

  async calculateEMI(principal_amount: number, interest_rate_annual: number, tenure_months: number) {
    const response = await this.client.post('/loans/calculate-emi', {
      principal_amount,
      interest_rate_annual,
      tenure_months,
    })
    return response.data
  }

  async createLoanApplication(course_id: number, university_id: number, expected_study_start: string) {
    const response = await this.client.post('/loans', {
      course_id,
      university_id,
      expected_study_start,
    })
    return response.data
  }

  async getLoanApplication(loan_id: number) {
    const response = await this.client.get(`/loans/${loan_id}`)
    return response.data
  }

  async getLoanApplications() {
    const response = await this.client.get('/loans')
    return response.data
  }

  async preQualifyLoan(loan_id: number) {
    const response = await this.client.post(`/loans/${loan_id}/pre-qualify`)
    return response.data
  }

  async submitLoanApplication(loan_id: number) {
    const response = await this.client.post(`/loans/${loan_id}/submit`)
    return response.data
  }

  async getLoanProducts(limit: number = 10) {
    const response = await this.client.get('/loans/products', { params: { limit } })
    return response.data
  }

  // ============================================================================
  // GROWTH ENGINE ENDPOINTS
  // ============================================================================

  async analyzeUser() {
    const response = await this.client.post('/growth/analyze')
    return response.data
  }

  async getRecommendations() {
    const response = await this.client.get('/growth/recommendations')
    return response.data
  }

  async getSegmentAnalysis(segment: string, limit: number = 10) {
    const response = await this.client.get('/growth/segment-analysis', {
      params: { segment, limit },
    })
    return response.data
  }

  // ============================================================================
  // RECOMMENDATION ENDPOINTS
  // ============================================================================

  async getRecommendedCourses(limit: number = 10) {
    const response = await this.client.get('/recommendations/courses', { params: { limit } })
    return response.data
  }

  async getCareerNavigator(selected_field: string, selected_country: string) {
    const response = await this.client.post('/recommendations/career-navigator', {
      selected_field,
      selected_country,
    })
    return response.data
  }

  async calculateROI(total_cost: number, loan_amount: number, interest_rate: number) {
    const response = await this.client.post('/recommendations/roi', {
      total_cost,
      loan_amount,
      interest_rate,
    })
    return response.data
  }

  // ============================================================================
  // COURSE/UNIVERSITY ENDPOINTS
  // ============================================================================

  async searchCourses(query: string, limit: number = 20) {
    const response = await this.client.get('/courses/search', { params: { q: query, limit } })
    return response.data
  }

  async getCourse(course_id: number) {
    const response = await this.client.get(`/courses/${course_id}`)
    return response.data
  }

  async searchUniversities(query: string, limit: number = 20) {
    const response = await this.client.get('/universities/search', { params: { q: query, limit } })
    return response.data
  }

  async getUniversity(university_id: number) {
    const response = await this.client.get(`/universities/${university_id}`)
    return response.data
  }

  async discoverCourses(
    field?: string,
    country?: string,
    min_ranking?: number,
    limit: number = 20
  ) {
    const response = await this.client.get('/courses/discover', {
      params: { field, country, min_ranking, limit },
    })
    return response.data
  }
}

export const apiClient = new APIClient()
export default apiClient
