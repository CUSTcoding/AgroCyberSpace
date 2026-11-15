import { createContext, useContext, useMemo, useState } from 'react'
import { translate, type Language } from '../i18n'
import type { Challenge } from '../types'
import { Icon, IconLabel } from './Icon'

const ChallengeLanguageContext = createContext<Language>('pt')

function useChallengeTranslate() {
  const language = useContext(ChallengeLanguageContext)
  return (text: string) => translate(text, language)
}

type Props = {
  challenge: Challenge
  onSolved: () => void
  strategy: 'A' | 'B' | 'C'
  setStrategy: (s: 'A' | 'B' | 'C') => void
  language: Language
}

export function Challenges({ challenge, onSolved, strategy, setStrategy, language }: Props) {
  return (
    <ChallengeLanguageContext.Provider value={language}>
    <div className="challenge-card">
      {challenge.type === 'mz-map' && <MzMap onSolved={onSolved} />}
      {challenge.type === 'tools' && <Tools onSolved={onSolved} />}
      {challenge.type === 'quiz' && <Quiz question={challenge.question} options={challenge.options} onSolved={onSolved} />}
      {challenge.type === 'multi-quiz' && <MultiQuiz questions={challenge.questions} onSolved={onSolved} />}
      {challenge.type === 'plant-sim' && <PlantSim onSolved={onSolved} />}
      {challenge.type === 'moisture-zones' && (
        <Quiz
          question="Qual zona está mais seca?"
          options={[
            { icon: 'mountain', label: 'Zona A 0.08', correct: true },
            { icon: 'leaf', label: 'Zona B 0.21' },
            { icon: 'droplet', label: 'Zona C 0.35' },
          ]}
          onSolved={onSolved}
        />
      )}
      {challenge.type === 'water-split' && <WaterSplit onSolved={onSolved} />}
      {challenge.type === 'ndvi' && <NdviLab onSolved={onSolved} />}
      {challenge.type === 'ndvi-map' && (
        <Quiz
          question="Qual zona tem o menor NDVI?"
          options={[
            { icon: 'status-green', label: 'A 0.72' },
            { icon: 'status-brown', label: 'B 0.18', correct: true },
            { icon: 'status-yellow', label: 'C 0.51' },
          ]}
          onSolved={onSolved}
        />
      )}
      {challenge.type === 'soil-texture' && <SoilTexture onSolved={onSolved} />}
      {challenge.type === 'practices' && <Practices onSolved={onSolved} />}
      {challenge.type === 'erosion' && <Erosion onSolved={onSolved} />}
      {challenge.type === 'notebook' && <Notebook onSolved={onSolved} />}
      {challenge.type === 'crop-water' && <CropWater onSolved={onSolved} />}
      {challenge.type === 'priorities' && <Priorities onSolved={onSolved} />}
      {challenge.type === 'rotation-build' && <RotationBuild onSolved={onSolved} />}
      {challenge.type === 'climate-lab' && <ClimateLab onSolved={onSolved} />}
      {challenge.type === 'rotation-compare' && <RotationCompare onSolved={onSolved} />}
      {challenge.type === 'uncertainty' && (
        <Quiz
          question="X tem 2,4 (1,4–3,4). Y tem 2,2 (1,9–2,5). O que é mais certo?"
          options={[
            { icon: 'trophy', label: 'X é sempre melhor' },
            { icon: 'scale', label: 'X é mais alto, mas mais incerto', correct: true },
            { icon: 'lock', label: 'Y garante 1,9 sempre' },
          ]}
          onSolved={onSolved}
        />
      )}
      {challenge.type === 'checklist' && <Checklist items={challenge.items} onSolved={onSolved} />}
      {challenge.type === 'pick-strategy' && (
        <PickStrategy value={strategy} onPick={setStrategy} onSolved={onSolved} />
      )}
      {challenge.type === 'extreme-sim' && <ExtremeSim onSolved={onSolved} />}
      {challenge.type === 'resilience' && <Resilience onSolved={onSolved} />}
      {challenge.type === 'timeline' && <Timeline onSolved={onSolved} strategy={strategy} />}
      {challenge.type === 'sources' && <Sources onSolved={onSolved} />}
      {challenge.type === 'harvest-econ' && <HarvestEcon onSolved={onSolved} />}
      {challenge.type === 'report' && (
        <PickStrategy value={strategy} onPick={setStrategy} onSolved={onSolved} report />
      )}
    </div>
    </ChallengeLanguageContext.Provider>
  )
}

function Feedback({ ok, text }: { ok: boolean | null; text: string }) {
  const t = useChallengeTranslate()
  if (ok === null) return null
  return <p className={`fb ${ok ? 'ok' : 'bad'}`}><Icon name={ok ? 'check' : 'repeat'} /> {t(text)}</p>
}

function Quiz({
  question,
  questionSuffix = '',
  options,
  onSolved,
}: {
  question: string
  questionSuffix?: string
  options: { icon: string; label: string; correct?: boolean }[]
  onSolved: () => void
}) {
  const [ok, setOk] = useState<boolean | null>(null)
  const t = useChallengeTranslate()
  return (
    <div>
      <h3>{t(question)}{questionSuffix}</h3>
      <div className="choice-grid">
        {options.map((o) => (
          <button
            key={o.label}
            className="pic-btn"
            onClick={() => {
              setOk(!!o.correct)
              if (o.correct) onSolved()
            }}
          >
            <span className="pic"><Icon name={o.icon} /></span>
            <span>{t(o.label)}</span>
          </button>
        ))}
      </div>
      <Feedback ok={ok} text={ok ? 'Boa!' : 'Tenta outro desenho.'} />
    </div>
  )
}

function MultiQuiz({
  questions,
  onSolved,
}: {
  questions: { question: string; options: { icon: string; label: string; correct?: boolean }[] }[]
  onSolved: () => void
}) {
  const [i, setI] = useState(0)
  const q = questions[i]
  return (
    <Quiz
      question={q.question}
      questionSuffix={`  (${i + 1}/${questions.length})`}
      options={q.options}
      onSolved={() => {
        const next = i + 1
        if (next >= questions.length) onSolved()
        else setI(next)
      }}
    />
  )
}

function MzMap({ onSolved }: { onSolved: () => void }) {
  const [ok, setOk] = useState<boolean | null>(null)
  const t = useChallengeTranslate()
  const places = [
    { id: 'ao', label: 'Angola', x: 18, y: 42 },
    { id: 'tz', label: 'Tanzânia', x: 58, y: 28 },
    { id: 'mz', label: 'Moçambique', x: 62, y: 52, good: true },
    { id: 'za', label: 'África do Sul', x: 42, y: 78 },
    { id: 'mg', label: 'Madagáscar', x: 84, y: 58 },
  ]
  return (
    <div>
      <h3>{t('Toca em Moçambique')}</h3>
      <div className="africa-map">
        {places.map((p) => (
          <button
            key={p.id}
            className={`map-pin ${p.id === 'mz' ? 'mz' : ''}`}
            style={{ left: `${p.x}%`, top: `${p.y}%` }}
            onClick={() => {
              setOk(!!p.good)
              if (p.good) onSolved()
            }}
          >
            <Icon name={p.id === 'mz' ? 'flag-mozambique' : 'map-pin'} />
            {t(p.label)}
          </button>
        ))}
      </div>
      <Feedback ok={ok} text={ok ? 'Encontraste Moçambique!' : 'Ainda não. Procura a bandeira.'} />
    </div>
  )
}

function Tools({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const tools = [
    { icon: 'cloud-rain', name: 'GPM', text: 'Chuva' },
    { icon: 'thermometer', name: 'POWER', text: 'Calor' },
    { icon: 'droplet', name: 'SMAP', text: 'Solo húmido' },
    { icon: 'leaf', name: 'Landsat', text: 'Plantas' },
  ]
  const [seen, setSeen] = useState<string[]>([])
  return (
    <div>
      <h3>{tr('Toca nas 4 ferramentas')}</h3>
      <div className="choice-grid four">
        {tools.map((t) => (
          <button
            key={t.name}
            className={`pic-btn ${seen.includes(t.name) ? 'picked' : ''}`}
            onClick={() => {
              const next = seen.includes(t.name) ? seen : [...seen, t.name]
              setSeen(next)
              if (next.length === 4) onSolved()
            }}
          >
            <span className="pic"><Icon name={t.icon} /></span>
            <b>{t.name}</b>
            <span>{tr(t.text)}</span>
          </button>
        ))}
      </div>
      <p className="hint">{seen.length}/4</p>
    </div>
  )
}

function PlantSim({ onSolved }: { onSolved: () => void }) {
  const t = useChallengeTranslate()
  const [temp, setTemp] = useState(36)
  const [water, setWater] = useState(45)
  const [mulch, setMulch] = useState(false)
  const risk = Math.min(100, Math.round((temp - 20) * 2.2 + (100 - water) * 0.5 - (mulch ? 12 : 0)))
  return (
    <div>
      <h3>{t('Protege a planta')}</h3>
      <div className="plant-face"><Icon name={risk > 70 ? 'wilted-flower' : risk > 45 ? 'sprout' : 'leaf'} /></div>
      <label>{t('Temperatura')} {temp}°C
        <input type="range" min={25} max={45} value={temp} onChange={(e) => setTemp(+e.target.value)} />
      </label>
      <label>{t('Água')} {water}%
        <input type="range" min={10} max={90} value={water} onChange={(e) => setWater(+e.target.value)} />
      </label>
      <button className={`pic-btn ${mulch ? 'picked' : ''}`} onClick={() => setMulch(!mulch)}>
        <Icon name="log" /> {t('Cobertura morta')}
      </button>
      <p className="hint">{t('Risco ilustrativo:')} {risk}/100 — {t('não é modelo real.')}</p>
      <button className="cta" onClick={onSolved}>{t('Percebi')}</button>
    </div>
  )
}

function WaterSplit({ onSolved }: { onSolved: () => void }) {
  const t = useChallengeTranslate()
  return (
    <div>
      <h3>{t('Para onde foi a água?')}</h3>
      <div className="bars">
        <div><span><Icon name="arrow-down" /> {t('Infiltração')}</span><i style={{ width: '50%' }} /></div>
        <div><span><Icon name="sun" /> {t('Evaporação')}</span><i style={{ width: '25%' }} /></div>
        <div><span><Icon name="arrow-right" /> {t('Escoamento')}</span><i style={{ width: '25%' }} /></div>
      </div>
      <p className="hint">{t('Nem toda a chuva fica na terra para as raízes.')}</p>
      <button className="cta" onClick={onSolved}>{t('Percebi')}</button>
    </div>
  )
}

function NdviLab({ onSolved }: { onSolved: () => void }) {
  const t = useChallengeTranslate()
  const [nir, setNir] = useState(0.6)
  const [red, setRed] = useState(0.15)
  const ndvi = (nir - red) / (nir + red)
  return (
    <div>
      <h3>{t('Descodifica o NDVI')}</h3>
      <p className="big-num">{ndvi.toFixed(2)}</p>
      <label>{t('Infravermelho')} {nir.toFixed(2)}
        <input type="range" min={0.1} max={0.9} step={0.01} value={nir} onChange={(e) => setNir(+e.target.value)} />
      </label>
      <label>{t('Vermelho')} {red.toFixed(2)}
        <input type="range" min={0.05} max={0.6} step={0.01} value={red} onChange={(e) => setRed(+e.target.value)} />
      </label>
      <p className="hint">{t(ndvi > 0.5 ? 'Sinal de vegetação vigorosa (exemplo).' : 'Sinal mais fraco (exemplo).')}</p>
      <button className="cta" onClick={onSolved}>{t('Percebi')}</button>
    </div>
  )
}

function SoilTexture({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const soils = [
    { id: 'areia', icon: 'umbrella', t: 'Arenoso', d: 'Deixa a água passar depressa.' },
    { id: 'franco', icon: 'potted-plant', t: 'Franco', d: 'Mistura equilibrada.' },
    { id: 'argila', icon: 'brick', t: 'Argiloso', d: 'Guarda água, pode compactar.' },
  ]
  const [id, setId] = useState('franco')
  const s = soils.find((x) => x.id === id)!
  return (
    <div>
      <h3>{tr('Explorador do solo')}</h3>
      <div className="choice-grid">
        {soils.map((x) => (
          <button key={x.id} className={`pic-btn ${id === x.id ? 'picked' : ''}`} onClick={() => setId(x.id)}>
            <span className="pic"><Icon name={x.icon} /></span>{tr(x.t)}
          </button>
        ))}
      </div>
      <p className="hint">{tr(s.d)}</p>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}

function Practices({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const items = [
    { id: 'mulch', icon: 'log', t: 'Cobertura morta', good: true },
    { id: 'compost', icon: 'falling-leaf', t: 'Composto', good: true },
    { id: 'rot', icon: 'refresh', t: 'Rotação', good: true },
    { id: 'bare', icon: 'mountain', t: 'Solo nu', good: false },
  ]
  const [sel, setSel] = useState<string[]>(['mulch'])
  const score = items.filter((i) => i.good && sel.includes(i.id)).length * 25 - (sel.includes('bare') ? 20 : 0)
  return (
    <div>
      <h3>{tr('Constrói um solo saudável')}</h3>
      <div className="choice-grid four">
        {items.map((i) => (
          <button
            key={i.id}
            className={`pic-btn ${sel.includes(i.id) ? 'picked' : ''}`}
            onClick={() => setSel(sel.includes(i.id) ? sel.filter((x) => x !== i.id) : [...sel, i.id])}
          >
            <span className="pic"><Icon name={i.icon} /></span>{tr(i.t)}
          </button>
        ))}
      </div>
      <p className="hint">{tr('Índice de jogo:')} {Math.max(0, score)}/100</p>
      <button className="cta" onClick={onSolved}>{tr('Guardar práticas')}</button>
    </div>
  )
}

function Erosion({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const [slope, setSlope] = useState(12)
  const [cover, setCover] = useState(30)
  const [rain, setRain] = useState(2)
  const risk = Math.min(100, Math.round(slope * 2 + rain * 18 - cover * 0.7))
  return (
    <div>
      <h3>{tr('Protege a machamba')}</h3>
      <label>{tr('Declive')} {slope}°
        <input type="range" min={0} max={30} value={slope} onChange={(e) => setSlope(+e.target.value)} />
      </label>
      <label>{tr('Cobertura')} {cover}%
        <input type="range" min={0} max={100} value={cover} onChange={(e) => setCover(+e.target.value)} />
      </label>
      <div className="choice-grid">
        {['Fraca', 'Moderada', 'Intensa'].map((n, i) => (
          <button key={n} className={`pic-btn ${rain === i + 1 ? 'picked' : ''}`} onClick={() => setRain(i + 1)}>
            <Icon name={['cloud-sun-rain', 'cloud-rain', 'cloud-lightning'][i]} /> {tr(n)}
          </button>
        ))}
      </div>
      <p className="hint">{tr('Risco ilustrativo:')} {Math.max(5, risk)}/100</p>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}

function Notebook({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  return (
    <div>
      <h3>{tr('Caderno da machamba')}</h3>
      <p className="hint">{tr('Toca no que viste. Isto é um desenho, não uma análise de laboratório.')}</p>
      <div className="choice-grid four">
        {[
          ['umbrella', 'Areia'],
          ['potted-plant', 'Franco'],
          ['brick', 'Argila'],
          ['help-circle', 'Ainda não sei'],
        ].map(([i, t]) => (
          <button key={t} className="pic-btn">
            <span className="pic"><Icon name={i} /></span>{tr(t)}
          </button>
        ))}
      </div>
      <button className="cta" onClick={onSolved}>{tr('Guardar ficha')}</button>
    </div>
  )
}

function CropWater({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const crops = [
    { id: 'milho', icon: 'maize', t: 'Milho' },
    { id: 'nhemba', icon: 'bean', t: 'Nhemba' },
    { id: 'sorgo', icon: 'wheat', t: 'Sorgo' },
    { id: 'amendoim', icon: 'peanut', t: 'Amendoim' },
  ]
  const [c, setC] = useState('milho')
  const [w, setW] = useState(1)
  const note =
    w === 0
      ? 'Risco de falta de água, sobretudo em fases sensíveis.'
      : w === 1
        ? 'Água limitada: comparar variedades e datas.'
        : 'Água mais favorável, mas o solo e as pragas continuam a importar.'
  return (
    <div>
      <h3>{tr('Cultura e água')}</h3>
      <div className="choice-grid four">
        {crops.map((x) => (
          <button key={x.id} className={`pic-btn ${c === x.id ? 'picked' : ''}`} onClick={() => setC(x.id)}>
            <span className="pic"><Icon name={x.icon} /></span>{tr(x.t)}
          </button>
        ))}
      </div>
      <div className="choice-grid">
        {['Pouca', 'Média', 'Muita'].map((n, i) => (
          <button key={n} className={`pic-btn ${w === i ? 'picked' : ''}`} onClick={() => setW(i)}>
            {tr(n)}
          </button>
        ))}
      </div>
      <p className="hint">{tr(note)}</p>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}

function Priorities({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const all = [
    { id: 'water', icon: 'droplet', t: 'Água' },
    { id: 'food', icon: 'cooking-pot', t: 'Comida' },
    { id: 'soil', icon: 'sprout', t: 'Solo' },
    { id: 'market', icon: 'cart', t: 'Venda' },
    { id: 'seed', icon: 'nut', t: 'Sementes' },
  ]
  const [sel, setSel] = useState<string[]>(['water', 'food', 'soil'])
  return (
    <div>
      <h3>{tr('Até 3 prioridades')}</h3>
      <div className="choice-grid">
        {all.map((x) => (
          <button
            key={x.id}
            className={`pic-btn ${sel.includes(x.id) ? 'picked' : ''}`}
            onClick={() => {
              if (sel.includes(x.id)) setSel(sel.filter((i) => i !== x.id))
              else if (sel.length < 3) setSel([...sel, x.id])
            }}
          >
            <span className="pic"><Icon name={x.icon} /></span>{tr(x.t)}
          </button>
        ))}
      </div>
      <p className="hint">{sel.length}/3</p>
      <button className="cta" disabled={sel.length === 0} onClick={onSolved}>{tr('Guardar')}</button>
    </div>
  )
}

function RotationBuild({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const crops = [
    { icon: 'maize', label: 'Milho' },
    { icon: 'bean', label: 'Nhemba' },
    { icon: 'wheat', label: 'Sorgo' },
    { icon: 'peanut', label: 'Amendoim' },
  ]
  const [seq, setSeq] = useState([0, 1, 2])
  return (
    <div>
      <h3>{tr('Três campanhas')}</h3>
      {seq.map((v, i) => (
        <div key={i} className="choice-grid four">
          {crops.map((crop, ci) => (
            <button key={crop.label} className={`pic-btn ${v === ci ? 'picked' : ''}`} onClick={() => setSeq(seq.map((x, xi) => (xi === i ? ci : x)))}>
              <span className="pic"><Icon name={crop.icon} /></span>
              {tr(crop.label)}
            </button>
          ))}
        </div>
      ))}
      <button className="cta" onClick={onSolved}>{tr('Guardar sequência')}</button>
    </div>
  )
}

function ClimateLab({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const scenes = [
    { t: 'Seco', gpm: 390, temp: 37, smap: 0.1, ndvi: 0.31 },
    { t: 'Médio', gpm: 620, temp: 32, smap: 0.2, ndvi: 0.48 },
    { t: 'Húmido', gpm: 880, temp: 29, smap: 0.31, ndvi: 0.62 },
  ]
  const [i, setI] = useState(0)
  const s = scenes[i]
  return (
    <div>
      <h3>{tr('Laboratório climático')}</h3>
      <div className="choice-grid">
        {scenes.map((x, n) => (
          <button key={x.t} className={`pic-btn ${i === n ? 'picked' : ''}`} onClick={() => setI(n)}>{tr(x.t)}</button>
        ))}
      </div>
      <div className="stat-grid">
        <div><Icon name="cloud-rain" /> {s.gpm} mm</div>
        <div><Icon name="thermometer" /> {s.temp}°C</div>
        <div><Icon name="droplet" /> {s.smap}</div>
        <div><Icon name="leaf" /> {s.ndvi}</div>
      </div>
      <p className="hint">{tr('Valores fictícios para aprender, não dados reais da NASA.')}</p>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}

function RotationCompare({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const [w, setW] = useState([4, 5, 3, 2])
  const labels = ['droplet Água', 'cooking-pot Comida', 'sprout Solo', 'cart Mercado']
  const scores = useMemo(() => {
    const base = [
      [2, 5, 2, 3],
      [4, 4, 4, 3],
      [5, 3, 4, 4],
    ]
    return base.map((b) => Math.round((b.reduce((s, v, i) => s + v * w[i], 0) / (w.reduce((a, b) => a + b, 0) * 5)) * 100))
  }, [w])
  const names = ['A milho-milho-milho', 'B milho-nhemba-sorgo', 'C sorgo-nhemba-amendoim']
  const best = scores.indexOf(Math.max(...scores))
  return (
    <div>
      <h3>{tr('Comparador de rotações')}</h3>
      {labels.map((l, i) => (
        <label key={l}><IconLabel text={tr(l)} /> {w[i]}
          <input type="range" min={1} max={5} value={w[i]} onChange={(e) => setW(w.map((x, xi) => (xi === i ? +e.target.value : x)))} />
        </label>
      ))}
      <div className="stat-grid">
        {names.map((n, i) => (
          <div key={n} className={i === best ? 'best' : ''}>{tr(n)}: {scores[i]}</div>
        ))}
      </div>
      <p className="hint">{tr('Pontuação de jogo. Não é rendimento real.')}</p>
      <button className="cta" onClick={onSolved}>{tr('Continuar')}</button>
    </div>
  )
}

function Checklist({ items, onSolved }: { items: { icon: string; label: string }[]; onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const [sel, setSel] = useState<string[]>([])
  return (
    <div>
      <h3>{tr('O que já verificámos?')}</h3>
      <div className="choice-grid">
        {items.map((it) => (
          <button
            key={it.label}
            className={`pic-btn ${sel.includes(it.label) ? 'picked' : ''}`}
            onClick={() => setSel(sel.includes(it.label) ? sel.filter((x) => x !== it.label) : [...sel, it.label])}
          >
            <span className="pic"><Icon name={it.icon} /></span>{tr(it.label)}
          </button>
        ))}
      </div>
      <p className="hint">{sel.length}/{items.length}</p>
      <button className="cta" onClick={onSolved}>{tr('Seguir')}</button>
    </div>
  )
}

function PickStrategy({
  value,
  onPick,
  onSolved,
  report,
}: {
  value: 'A' | 'B' | 'C'
  onPick: (s: 'A' | 'B' | 'C') => void
  onSolved: () => void
  report?: boolean
}) {
  const tr = useChallengeTranslate()
  const opts = [
    { id: 'A' as const, icon: 'maize', t: 'A · só milho' },
    { id: 'B' as const, icon: 'crop-mix', t: 'B · milho, nhemba, sorgo' },
    { id: 'C' as const, icon: 'rotation-crops', t: 'C · sorgo, nhemba, amendoim' },
  ]
  return (
    <div>
      <h3>{tr(report ? 'Legado da comunidade' : 'Qual investigar?')}</h3>
      <div className="choice-grid">
        {opts.map((o) => (
          <button key={o.id} className={`pic-btn ${value === o.id ? 'picked' : ''}`} onClick={() => onPick(o.id)}>
            <span className="pic"><Icon name={o.icon} /></span>{tr(o.t)}
          </button>
        ))}
      </div>
      {report && <p className="hint">{tr('Justificação: manter comida, diversificar e testar no terreno.')}</p>}
      <button className="cta" onClick={onSolved}>{tr('Registar')}</button>
    </div>
  )
}

function ExtremeSim({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const scenes = [
    { t: 'Seca', icon: 'cactus', rain: 260, temp: 36, smap: 0.09, ndvi: 0.27 },
    { t: 'Calor', icon: 'flame', rain: 500, temp: 41, smap: 0.14, ndvi: 0.33 },
    { t: 'Chuva forte', icon: 'waves', rain: 920, temp: 28, smap: 0.34, ndvi: 0.44 },
  ]
  const [i, setI] = useState(0)
  const s = scenes[i]
  return (
    <div>
      <h3>{tr('Simulador de extremos')}</h3>
      <div className="choice-grid">
        {scenes.map((x, n) => (
          <button key={x.t} className={`pic-btn ${i === n ? 'picked' : ''}`} onClick={() => setI(n)}>
            <span className="pic"><Icon name={x.icon} /></span>{tr(x.t)}
          </button>
        ))}
      </div>
      <div className="stat-grid">
        <div><Icon name="cloud-rain" /> {s.rain} mm</div>
        <div><Icon name="thermometer" /> {s.temp}°C</div>
        <div><Icon name="droplet" /> {s.smap}</div>
        <div><Icon name="leaf" /> {s.ndvi}</div>
      </div>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}

function Resilience({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const [i, setI] = useState(0)
  const table = [
    [35, 70, 78],
    [40, 66, 60],
    [48, 72, 55],
  ]
  const names = ['A', 'B', 'C']
  return (
    <div>
      <h3>{tr('Teste de resiliência')}</h3>
      <div className="choice-grid">
        {['cactus Seca', 'flame Calor', 'waves Cheia'].map((n, nI) => (
          <button key={n} className={`pic-btn ${i === nI ? 'picked' : ''}`} onClick={() => setI(nI)}><IconLabel text={tr(n)} /></button>
        ))}
      </div>
      <div className="stat-grid">
        {names.map((n, ni) => <div key={n}>{n}: {table[i][ni]}/100</div>)}
      </div>
      <p className="hint">{tr('A ordem muda com a ameaça. Números de jogo.')}</p>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}

function Timeline({ onSolved, strategy }: { onSolved: () => void; strategy: 'A' | 'B' | 'C' }) {
  const tr = useChallengeTranslate()
  const phases = [
    { icon: 'nut', t: 'Preparar' },
    { icon: 'sprout', t: 'Crescer' },
    { icon: 'flower', t: 'Florir' },
    { icon: 'basket', t: 'Colher' },
  ]
  const [i, setI] = useState(0)
  return (
    <div>
      <h3>{tr('Diário da machamba ·')}{strategy}</h3>
      <div className="choice-grid four">
        {phases.map((p, n) => (
          <button key={p.t} className={`pic-btn ${i === n ? 'picked' : ''}`} onClick={() => setI(n)}>
            <span className="pic"><Icon name={p.icon} /></span>{tr(p.t)}
          </button>
        ))}
      </div>
      <button className="cta" onClick={onSolved}>{tr('Vi as 4 fases')}</button>
    </div>
  )
}

function Sources({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const all = [
    { id: 'gpm', icon: 'cloud-rain', t: 'GPM chuva' },
    { id: 'power', icon: 'thermometer', t: 'POWER calor' },
    { id: 'smap', icon: 'droplet', t: 'SMAP solo' },
    { id: 'landsat', icon: 'leaf', t: 'Landsat plantas' },
    { id: 'local', icon: 'hand', t: 'Olhos no terreno' },
  ]
  const [sel, setSel] = useState<string[]>([])
  const done = all.every((x) => sel.includes(x.id))
  return (
    <div>
      <h3>{tr('Que fontes usar?')}</h3>
      <div className="choice-grid">
        {all.map((x) => (
          <button
            key={x.id}
            className={`pic-btn ${sel.includes(x.id) ? 'picked' : ''}`}
            onClick={() => {
              const next = sel.includes(x.id) ? sel.filter((i) => i !== x.id) : [...sel, x.id]
              setSel(next)
              if (all.every((a) => next.includes(a.id))) onSolved()
            }}
          >
            <span className="pic"><Icon name={x.icon} /></span>{tr(x.t)}
          </button>
        ))}
      </div>
      <p className="hint">{tr(done ? 'Os satélites e o terreno juntos.' : 'Falta alguma fonte.')}</p>
    </div>
  )
}

function HarvestEcon({ onSolved }: { onSolved: () => void }) {
  const tr = useChallengeTranslate()
  const [p, setP] = useState([2.8, 4.5, 2.4, 6.5])
  const names = [
    { icon: 'maize', label: 'Milho' },
    { icon: 'bean', label: 'Nhemba' },
    { icon: 'wheat', label: 'Sorgo' },
    { icon: 'peanut', label: 'Amendoim' },
  ]
  return (
    <div>
      <h3>{tr('Preços de brincar (MZN/kg)')}</h3>
      {names.map((n, i) => (
        <label key={n.label}><Icon name={n.icon} /> {tr(n.label)} {p[i].toFixed(1)}
          <input type="range" min={1} max={10} step={0.1} value={p[i]} onChange={(e) => setP(p.map((x, xi) => (xi === i ? +e.target.value : x)))} />
        </label>
      ))}
      <p className="hint">{tr('Mudar o preço muda quem “ganha” no jogo. Não é mercado real.')}</p>
      <button className="cta" onClick={onSolved}>{tr('Percebi')}</button>
    </div>
  )
}
