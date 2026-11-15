export type Speaker = 'astronaut' | 'farmer' | 'amelia' | 'manual' | 'narrator' | 'child'

export type SceneId =
  | 'space'
  | 'ship'
  | 'hologram'
  | 'village'
  | 'farm'
  | 'dry'
  | 'heat'
  | 'rain'
  | 'soil'
  | 'lab'
  | 'academy'
  | 'storm'
  | 'harvest'
  | 'night'
  | 'council'

export type Reply = {
  icon: string
  label: string
  say: string
  action?: 'next' | 'repeat'
}

export type QuizOption = {
  icon: string
  label: string
  correct?: boolean
}

export type Challenge =
  | { type: 'mz-map' }
  | { type: 'tools' }
  | { type: 'quiz'; question: string; options: QuizOption[] }
  | { type: 'multi-quiz'; questions: { question: string; options: QuizOption[] }[] }
  | { type: 'plant-sim' }
  | { type: 'moisture-zones' }
  | { type: 'water-split' }
  | { type: 'ndvi' }
  | { type: 'ndvi-map' }
  | { type: 'soil-texture' }
  | { type: 'practices' }
  | { type: 'erosion' }
  | { type: 'notebook' }
  | { type: 'crop-water' }
  | { type: 'priorities' }
  | { type: 'rotation-build' }
  | { type: 'climate-lab' }
  | { type: 'rotation-compare' }
  | { type: 'uncertainty' }
  | { type: 'checklist'; items: { icon: string; label: string }[] }
  | { type: 'pick-strategy' }
  | { type: 'extreme-sim' }
  | { type: 'resilience' }
  | { type: 'timeline' }
  | { type: 'sources' }
  | { type: 'harvest-econ' }
  | { type: 'report' }

export type Slide = {
  id: string
  scene: SceneId
  speaker: Speaker
  text: string
  replies?: Reply[]
  challenge?: Challenge
}

export type Chapter = {
  id: number
  code: string
  title: string
  subtitle: string
  icon: string
  color: string
}

// Backend Integration Types
export type BackendHealth = {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'offline'
  api?: string
  environment?: string
  version?: string
  database?: {
    status: string
    latency_ms?: number
    error?: string | null
  }
  postgis?: {
    installed: boolean
    version?: string | null
  }
}

export type StudyRegion = {
  id: string
  code: string
  name: string
  province?: string
  description?: string
  center_lat?: number
  center_lon?: number
  is_proposed_study_area?: boolean
}

export type DistrictCropIndicator = {
  district_id: string
  district_name: string
  indicator_type: 'district_crop_stat'
  crop: string
  area_ha: number
  production_t: number
  campaign: string
  year: number
  source: string
  spatial_level: 'district'
  is_synthetic: boolean
}

export type AiHintResponse = {
  message_simple: string
  audio_text: string
  why: string
  limitations: string[]
  technical_details: {
    category: string
    source: string
    dataset_version: string
  }
  source?: string
  explanation?: string
  resolution_warning?: string | null
}
