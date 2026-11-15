import type { Language } from '../i18n'

type Props = {
  language: Language
  onChange: (language: Language) => void
  disabled?: boolean
}

export function LanguageSwitch({ language, onChange, disabled = false }: Props) {
  return (
    <div className="language-switch" role="group" aria-label="Language / Idioma">
      <button
        type="button"
        className={language === 'pt' ? 'selected' : ''}
        aria-label="Português"
        aria-pressed={language === 'pt'}
        disabled={disabled}
        onClick={() => onChange('pt')}
      >
        PT
      </button>
      <button
        type="button"
        className={language === 'en' ? 'selected' : ''}
        aria-label="English"
        aria-pressed={language === 'en'}
        disabled={disabled}
        onClick={() => onChange('en')}
      >
        EN
      </button>
    </div>
  )
}
