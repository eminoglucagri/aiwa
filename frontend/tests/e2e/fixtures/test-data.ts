export const testUsers = {
  valid: {
    email: process.env.TEST_EMAIL || 'test@example.com',
    password: process.env.TEST_PASSWORD || 'testpass123',
  },
  invalid: {
    noEmail: { password: 'testpass123' },
    noPassword: { email: 'test@example.com' },
    wrongPassword: { email: 'test@example.com', password: 'wrongpassword' },
    nonExistent: { email: 'nonexistent@example.com', password: 'testpass123' },
  },
  edge: {
    shortPassword: '123',
    longEmail: 'a'.repeat(100) + '@test.com',
    sqlInjection: "admin'--",
    xssAttempt: '<script>alert("xss")</script>',
  },
};

export const viewportSizes = {
  mobile: { width: 390, height: 844 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 720 },
};

export const apiBase = process.env.API_BASE_URL || 'https://api.your-domain.com';