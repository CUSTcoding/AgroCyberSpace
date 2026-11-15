import type { Language } from './i18n'

const KEY = 'agrospace-progress-v1'

export type Save = {
  completed: number[]
  chapter: number
  slide: number
  strategy: 'A' | 'B' | 'C'
  voice: boolean
  language: Language
  regionId?: string
  regionName?: string
}

const empty: Save = {
  completed: [],
  chapter: 0,
  slide: 0,
  strategy: 'B',
  voice: true,
  language: 'pt',
  regionId: '',
  regionName: '',
}

export function loadSave(): Save {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return { ...empty }
    return { ...empty, ...JSON.parse(raw) }
  } catch {
    return { ...empty }
  }
}

export function writeSave(save: Save) {
  try {
    localStorage.setItem(KEY, JSON.stringify(save))
  } catch {
    // ignore storage quota errors in restricted contexts
  }
}

export function isUnlocked(id: number, completed: number[]) {
  if (id === 1) return true
  return completed.includes(id - 1)
}
