import { useEffect, useRef, useState, type Dispatch, type SetStateAction } from 'react'
import { CHAPTERS } from '../content/chapters'
import { STORY } from '../content/story'
import { englishStory } from '../translations/story'
import type { Challenge, Reply, AiHintResponse } from '../types'
import type { Language } from '../i18n'
import { translate } from '../i18n'
import type { Save } from '../progress'
import { api } from '../services/api'
import { hush, speak } from '../speech'
import { Challenges } from './Challenges'
import { Icon } from './Icon'
import { LanguageSwitch } from './LanguageSwitch'
import { SceneArt } from './SceneArt'

const names = {
  astronaut: 'Astronauta',
  farmer: 'Agricultor',
  amelia: 'Dona Amélia',
  manual: 'Manual AgroSpace',
  narrator: 'História',
  child: 'Criança',
}

type Props = {
  chapter: number
  save: Save
  setSave: Dispatch<SetStateAction<Save>>
  language: Language
  onLanguageChange: (language: Language) => void
  onExit: () => void
}

export function PlayPage({ chapter, save, setSave, language, onLanguageChange, onExit }: Props) {
  const slides = STORY[chapter]
  const [i, setI] = useState(save.chapter === chapter ? save.slide : 0)
  const [solved, setSolved] = useState(false)
  const [echo, setEcho] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [aiHint, setAiHint] = useState<AiHintResponse | null>(null)
  const [loadingHint, setLoadingHint] = useState(false)
  const playbackId = useRef(0)
  const slide = slides[Math.min(i, slides.length - 1)]
  const ch = CHAPTERS[chapter - 1]
  const t = (text: string) => translate(text, language)
  const translatedStory = language === 'en' ? englishStory[slide.id] : undefined
  const displayText = translatedStory?.text ?? slide.text
  const displayReplies = (slide.replies || []).map((reply, index) => {
    const translatedReply = translatedStory?.replies?.[index]
    return language === 'en'
      ? {
          ...reply,
          label: translatedReply?.label ?? t(reply.label),
          say: translatedReply?.say ?? t(reply.say),
        }
      : reply
  })
  const displayChallenge = slide.challenge ? translateChallenge(slide.challenge, language) : undefined
  const needsChallenge = !!slide.challenge && !solved

  useEffect(() => {
    setSolved(false)
    setEcho(null)
    setBusy(false)
    setAiHint(null)
    setLoadingHint(false)
    setSave((s) => ({ ...s, chapter, slide: i }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chapter, i])

  useEffect(() => {
    playbackId.current += 1
    if (save.voice) void speak(displayText, language)
    return () => {
      playbackId.current += 1
      hush()
    }
  }, [displayText, language, save.voice])

  const finish = () => {
    const completed = save.completed.includes(chapter) ? save.completed : [...save.completed, chapter]
    setSave({ ...save, completed, chapter: 0, slide: 0 })
    onExit()
  }

  const next = () => {
    if (i >= slides.length - 1) finish()
    else setI(i + 1)
  }

  const onReply = (r: Reply) => {
    if (busy) return
    if (r.action === 'repeat') {
      if (save.voice) speak(displayText, language)
      return
    }
    if (needsChallenge) return
    if (r.say) {
      setBusy(true)
      setEcho(r.say)
      const currentPlayback = playbackId.current
      const advance = () => {
        if (playbackId.current === currentPlayback) next()
      }
      if (save.voice) void speak(r.say, language).then(advance)
      else window.setTimeout(advance, 1100)
    } else next()
  }

  const fetchAiHint = async () => {
    if (loadingHint) return
    setLoadingHint(true)
    const category = chapter <= 3 ? 'meteorology' : chapter <= 6 ? 'vegetation' : chapter <= 9 ? 'soil' : 'solar'
    try {
      const hint = await api.getAiHint(category, language)
      setAiHint(hint)
    } catch {
      setAiHint(null)
    } finally {
      setLoadingHint(false)
    }
  }

  return (
    <div className="play">
      <SceneArt scene={slide.scene} speaker={echo ? 'farmer' : slide.speaker} />
      <div className="play-top">
        <button className="ghost" onClick={onExit}><Icon name="←" /> {t('Missões')}</button>
        <div className="progress-dots" aria-label={`${t('Cena')} ${i + 1} ${t('de')} ${slides.length}`} role="img">
          {slides.map((s, n) => (
            <i key={s.id} className={n === i ? 'now' : n < i ? 'did' : ''} />
          ))}
        </div>
        <div className="play-actions">
          <LanguageSwitch language={language} onChange={onLanguageChange} disabled={busy} />
          <div className="ch-label">
            <Icon name={ch.icon} /> {ch.code} {t(ch.subtitle)}
          </div>
        </div>
      </div>

      {displayChallenge && (
        <div className="challenge-wrap">
          <Challenges
            challenge={displayChallenge}
            language={language}
            strategy={save.strategy}
            setStrategy={(strategy) => setSave({ ...save, strategy })}
            onSolved={() => setSolved(true)}
          />
        </div>
      )}

      <aside className="dock">
        <div className="dock-head">
          <b><Icon name={echo ? '👨‍🌾' : face(slide.speaker)} /> {echo ? t('Agricultor') : t(names[slide.speaker])}</b>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {needsChallenge && (
              <button
                className="hint-btn"
                onClick={fetchAiHint}
                disabled={loadingHint}
                type="button"
                title={t('Dica Científica da Missão')}
              >
                <Icon name="💡" />
                <span>{loadingHint ? t('A carregar dica...') : t('Pedir Dica IA')}</span>
              </button>
            )}
            <button
              className="voice-btn"
              aria-label={t(save.voice ? 'Desligar voz' : 'Ouvir a história')}
              aria-pressed={save.voice}
              disabled={busy}
              onClick={() => {
                const voice = !save.voice
                setSave((current) => ({ ...current, voice }))
                if (!voice) hush()
              }}
            >
              <Icon name={save.voice ? '🔊' : '🔇'} />
              <span className="voice-label">{t(save.voice ? 'Ouvir outra vez' : 'Ouvir a história')}</span>
            </button>
          </div>
        </div>

        {aiHint && (
          <div className="hint-box">
            <div className="hint-box-head">
              <span>🛰️ {t('Dica Científica da Missão')} ({aiHint.source})</span>
              <button
                type="button"
                onClick={() => setAiHint(null)}
                style={{ background: 'none', border: 'none', color: '#2ec4b6', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
            <p style={{ margin: '4px 0' }}>{aiHint.explanation}</p>
            {aiHint.resolution_warning && (
              <p style={{ fontSize: '11px', opacity: 0.8, margin: '2px 0 0' }}>⚠️ {aiHint.resolution_warning}</p>
            )}
          </div>
        )}

        <p className="line" aria-live="polite">{echo || displayText}</p>
        {needsChallenge ? (
          <p className="hint dock-hint"><Icon name="👆" /> {t('Toca nas imagens acima para continuar.')}</p>
        ) : (
          <div className="replies">
            {displayReplies.map((r) => (
              <button key={r.label} className="reply" onClick={() => onReply(r)} disabled={busy}>
                <Icon name={r.icon} />
                {r.label}
              </button>
            ))}
          </div>
        )}
        {solved && slide.challenge && (
          <button className="cta dock-cta" onClick={next}>{t('Seguir')} <Icon name="👉" /></button>
        )}
      </aside>
    </div>
  )
}

function translateChallenge(challenge: Challenge, language: Language): Challenge {
  if (language === 'pt') return challenge
  if (challenge.type === 'quiz') {
    return {
      ...challenge,
      question: translate(challenge.question, language),
      options: challenge.options.map((option) => ({ ...option, label: translate(option.label, language) })),
    }
  }
  if (challenge.type === 'multi-quiz') {
    return {
      ...challenge,
      questions: challenge.questions.map((question) => ({
        ...question,
        question: translate(question.question, language),
        options: question.options.map((option) => ({ ...option, label: translate(option.label, language) })),
      })),
    }
  }
  if (challenge.type === 'checklist') {
    return {
      ...challenge,
      items: challenge.items.map((item) => ({ ...item, label: translate(item.label, language) })),
    }
  }
  return challenge
}

function face(s: keyof typeof names) {
  return {
    astronaut: '🧑‍🚀',
    farmer: '👨‍🌾',
    amelia: '👵',
    manual: '📘',
    narrator: '✨',
    child: '👧',
  }[s]
}
