"use client"

import React from 'react'
import { useEarcons } from './EarconProvider'

export const EarconButton: React.FC<{ name: string; label?: string }> = ({ name, label }) => {
  const { play, enabled, setEnabled } = useEarcons()

  const handleClick = () => {
    // if user hasn't enabled, turn on (user action)
    if (!enabled) setEnabled(true)
    // play the named earcon (string typed) if available
    try { play(name as any) } catch (e) { /* degrade silently */ }
  }

  return (
    <button
      aria-label={label || `Play sound ${name}`}
      onClick={handleClick}
      style={{ minWidth: 64, minHeight: 64, padding: 12, borderRadius: 12 }}
    >
      {label || name}
    </button>
  )
}
