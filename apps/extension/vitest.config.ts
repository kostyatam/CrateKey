import { defineConfig } from 'vitest/config'

export default defineConfig({
  resolve: {
    alias: {
      // vitest-chrome's `main` is a CJS build that require()s vitest, which
      // vitest 2+ forbids — force the ESM build instead.
      'vitest-chrome': 'vitest-chrome/lib/index.esm.js',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['tests/setup.ts'],
    include: ['tests/**/*.test.ts'],
  },
})
