import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { ErrorBoundary } from '../src/components/eduboost/ErrorBoundary'

function Bomb() {
  throw new Error('boom')
}

test('ErrorBoundary catches error and shows message and retry', async () => {
  render(
    <ErrorBoundary title="Oops">
      <Bomb />
    </ErrorBoundary>
  )

  expect(await screen.findByText('Oops')).toBeInTheDocument()
  const retry = screen.getByRole('button', { name: /Try Again/i })
  expect(retry).toBeInTheDocument()
})

test('ErrorBoundary logs errors through componentDidCatch', async () => {
  const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

  render(
    <ErrorBoundary title="Oops">
      <Bomb />
    </ErrorBoundary>
  )

  expect(await screen.findByText('Oops')).toBeInTheDocument()
  expect(errorSpy).toHaveBeenCalled()

  errorSpy.mockRestore()
})
