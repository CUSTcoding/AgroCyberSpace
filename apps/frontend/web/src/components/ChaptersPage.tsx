import { CHAPTERS } from '../content/chapters'
import type { Language } from '../i18n'
import { translate } from '../i18n'
import { isUnlocked, type Save } from '../progress'
import type { BackendHealth, DistrictCropIndicator, StudyRegion } from '../types'
import { Icon } from './Icon'
import { LanguageSwitch } from './LanguageSwitch'

type Props = {
  save: Save
  backendHealth: BackendHealth
  regions: StudyRegion[]
  regionsState?: 'loading' | 'ready' | 'error'
  regionsError?: string
  indicators?: DistrictCropIndicator[]
  indicatorsState?: 'idle' | 'loading' | 'ready' | 'error'
  indicatorsError?: string
  onOpen: (id: number) => void
  onVoice: () => void
  onLanguageChange: (language: Language) => void
  onSelectRegion: (region: StudyRegion) => void
}

export function ChaptersPage({
  save,
  backendHealth,
  regions,
  onOpen,
  onVoice,
  onLanguageChange,
  onSelectRegion,
}: Props) {
  const t = (text: string) => translate(text, save.language)
  const isOnline = backendHealth.status === 'healthy' || backendHealth.status === 'degraded'

  return (
    <div className="chapters">
      <header className="topbar">
        <div className="brand">
          <span className="logo" aria-hidden="true"><Icon name="satellite" /></span>
          <div>
            <strong>AgroSpace</strong>
            <p>{t('Da Terra ao espaço. Do espaço à machamba.')}</p>
          </div>
        </div>
        <div className="topbar-actions">
          <span
            className={`backend-badge ${isOnline ? 'online' : 'offline'}`}
            title={
              isOnline
                ? `FastAPI v${backendHealth.version ?? '0.1.0'} - DB: ${backendHealth.database?.status ?? 'ok'}`
                : 'Backend API offline - Local mode active'
            }
          >
            <Icon name={isOnline ? 'satellite' : 'satellite'} />
            <span>
              {isOnline
                ? `${t('Conectado')}${save.regionName ? ` (${save.regionName})` : ''}`
                : t('Modo Offline')}
            </span>
          </span>

          <LanguageSwitch language={save.language} onChange={onLanguageChange} />
          <button
            className={`voice-btn ${save.voice ? 'on' : ''}`}
            onClick={onVoice}
            aria-label={t(save.voice ? 'Desligar voz' : 'Ligar voz')}
            aria-pressed={save.voice}
          >
            <Icon name={save.voice ? 'volume' : 'volume-off'} />
            <span className="voice-label">{t(save.voice ? 'Voz ligada' : 'Voz desligada')}</span>
          </button>
        </div>
      </header>
      <section className="hero-banner">
        <p className="kicker">{t('Aventura educativa · Moçambique')}</p>
        <h1>{t('Uma missão pela nossa machamba')}</h1>
        <p>{t('Toca numa missão. Ouve a história. Escolhe uma resposta.')}</p>

        {regions.length > 0 && (
          <div className="region-selector" aria-label={t('Região de Estudo')}>
            {regions.map((reg) => (
              <button
                key={reg.id}
                type="button"
                className={`region-chip ${save.regionId === reg.id ? 'active' : ''}`}
                onClick={() => onSelectRegion(reg)}
              >
                map-pin {reg.name}
              </button>
            ))}
          </div>
        )}

        <div className="hero-crew" aria-hidden="true">
          <span className="crew-star"><Icon name="sparkles" /></span>
          <span className="crew-person astronaut"><Icon name="user" /></span>
          <span className="crew-person farmer"><Icon name="user" /></span>
          <span className="crew-person amelia"><Icon name="elder" /></span>
          <span className="crew-person child"><Icon name="user" /></span>
          <span className="crew-star"><Icon name="sparkles" /></span>
        </div>
      </section>
      <div className="chapter-grid">
        {CHAPTERS.map((ch) => {
          const open = isUnlocked(ch.id, save.completed)
          const done = save.completed.includes(ch.id)
          return (
            <button
              key={ch.id}
              className={`chapter-card ${open ? 'open' : 'locked'} scene-thumb scene-${['space','hologram','rain','heat','soil','farm','soil','academy','lab','storm','council','harvest'][ch.id - 1]}`}
              disabled={!open}
              onClick={() => open && onOpen(ch.id)}
              style={{ ['--accent' as string]: ch.color }}
              aria-label={`${t('Missão')} ${ch.code}: ${t(ch.subtitle)}${done ? `, ${t('concluída')}` : ''}${!open ? `, ${t('bloqueada')}` : ''}`}
              title={open ? `${t('Começar')} ${t(ch.subtitle)}` : t('Conclui a anterior')}
            >
              <span className="ch-num">{t('MISSÃO')} {ch.code}</span>
              <span className="ch-icon" aria-hidden="true"><Icon name={open ? ch.icon : 'lock'} /></span>
              <span className="ch-sub">{t(ch.subtitle)}</span>
              <span className="ch-title">{t(done ? 'Jogar outra vez' : open ? 'Tocar para jogar' : 'Conclui a anterior')}</span>
              {done && <span className="done-pill" aria-label={t('Concluída')}><Icon name="✓" /></span>}
            </button>
          )
        })}
      </div>
    </div>
  )
}
