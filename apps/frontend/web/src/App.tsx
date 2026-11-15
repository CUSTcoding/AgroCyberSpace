import { useEffect, useState } from 'react'
import { ChaptersPage } from './components/ChaptersPage'
import { PlayPage } from './components/PlayPage'
import { translate } from './i18n'
import { loadSave, writeSave, type Save } from './progress'
import { api } from './services/api'
import type { BackendHealth, DistrictCropIndicator, StudyRegion } from './types'

export default function App() {
  const [save, setSave] = useState<Save>(() => loadSave())
  const [chapter, setChapter] = useState(0)
  const [backendHealth, setBackendHealth] = useState<BackendHealth>({ status: 'offline' })
  const [regions, setRegions] = useState<StudyRegion[]>([])
  const [regionsState, setRegionsState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [regionsError, setRegionsError] = useState('')
  const [indicators, setIndicators] = useState<DistrictCropIndicator[]>([])
  const [indicatorsState, setIndicatorsState] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle')
  const [indicatorsError, setIndicatorsError] = useState('')

  useEffect(() => {
    document.documentElement.lang = save.language
    document.title = translate('AgroSpace — Aventura na Machamba', save.language)
    writeSave(save)
  }, [save])

  useEffect(() => {
    let mounted = true
    async function loadBackendContext() {
      const health = await api.checkHealth()
      if (!mounted) return
      setBackendHealth(health)

      if (health.status === 'healthy' || health.status === 'degraded') {
        try {
          const remoteRegions = await api.getRegions()
          if (!mounted) return
          setRegions(remoteRegions)
          setRegionsState('ready')
          setSave((current) => {
            const selected = remoteRegions.find((region) => region.id === current.regionId) ?? remoteRegions[0]
            if (!selected) {
              return current.regionId || current.regionName
                ? { ...current, regionId: '', regionName: '' }
                : current
            }
            if (current.regionId === selected.id && current.regionName === selected.name) return current
            return { ...current, regionId: selected.id, regionName: selected.name }
          })
        } catch (error) {
          if (!mounted) return
          setRegions([])
          setRegionsState('error')
          setRegionsError(error instanceof Error ? error.message : 'Failed to load regions')
        }
      } else {
        setRegionsState('error')
        setRegionsError(health.database?.error ?? 'Backend unavailable')
      }
    }

    void loadBackendContext()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!save.regionId) {
      setIndicators([])
      setIndicatorsState('idle')
      setIndicatorsError('')
      return
    }

    let mounted = true
    setIndicatorsState('loading')
    setIndicatorsError('')
    api.getRegionIndicators(save.regionId)
      .then((items) => {
        if (!mounted) return
        setIndicators(items)
        setIndicatorsState('ready')
      })
      .catch((error: unknown) => {
        if (!mounted) return
        setIndicatorsState('error')
        setIndicatorsError(error instanceof Error ? error.message : 'Regional data unavailable')
      })
    return () => {
      mounted = false
    }
  }, [save.regionId])

  const handleSelectRegion = (region: StudyRegion) => {
    setSave((current) => ({
      ...current,
      regionId: region.id,
      regionName: region.name,
    }))
  }

  if (chapter) {
    return (
      <PlayPage
        chapter={chapter}
        save={save}
        setSave={setSave}
        language={save.language}
        onLanguageChange={(language) => setSave((current) => ({ ...current, language }))}
        onExit={() => setChapter(0)}
      />
    )
  }

  return (
    <ChaptersPage
      save={save}
      backendHealth={backendHealth}
      regions={regions}
      regionsState={regionsState}
      regionsError={regionsError}
      indicators={indicators}
      indicatorsState={indicatorsState}
      indicatorsError={indicatorsError}
      onOpen={setChapter}
      onVoice={() => setSave((current) => ({ ...current, voice: !current.voice }))}
      onLanguageChange={(language) => setSave((current) => ({ ...current, language }))}
      onSelectRegion={handleSelectRegion}
    />
  )
}
