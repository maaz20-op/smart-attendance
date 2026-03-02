import { http, HttpResponse } from 'msw'

export const handlers = [
  // Auth mock
  http.post('*/api/v1/auth/login', async ({ request }) => {
    return HttpResponse.json({
      access_token: 'mock-token-123',
      token_type: 'bearer',
      user: {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'student'
      }
    })
  }),

  http.get('*/api/v1/auth/me', () => {
    return HttpResponse.json({
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'student'
    })
  }),

  // Attendance mock
  http.post('*/api/v1/attendance/mark', () => {
    return HttpResponse.json({
        message: 'Attendance marked successfully',
        status: 'present',
        confidence: 0.95
    })
  }),

  http.get('*/api/v1/attendance/history', () => {
    return HttpResponse.json([
        {
            date: '2023-10-01',
            status: 'present',
            subject: 'Mathematics'
        }
    ])
  })
]
