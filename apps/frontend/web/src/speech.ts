import type { Language } from './i18n'

const voicesReady = new Promise<void>((resolve) => {
  if (typeof speechSynthesis === 'undefined') {
    resolve()
    return
  }
  const done = () => resolve()
  speechSynthesis.addEventListener('voiceschanged', done, { once: true })
  if (speechSynthesis.getVoices().length) done()
  setTimeout(done, 800)
})

export async function speak(text: string, language: Language = 'pt'): Promise<void> {
  if (typeof speechSynthesis === 'undefined') return
  await voicesReady
  speechSynthesis.cancel()
  await new Promise<void>((resolve) => {
    const utter = new SpeechSynthesisUtterance(text)
    const voices = speechSynthesis.getVoices()
    const prefix = language === 'en' ? 'en' : 'pt'
    const voice = voices.find((v) => v.lang.toLowerCase().startsWith(prefix))
    if (voice) utter.voice = voice
    utter.lang = voice?.lang || (language === 'en' ? 'en-US' : 'pt-PT')
    utter.rate = 0.92
    utter.pitch = 1
    utter.onend = () => resolve()
    utter.onerror = () => resolve()
    speechSynthesis.speak(utter)
  })
}

export function hush() {
  if (typeof speechSynthesis === 'undefined') return
  speechSynthesis.cancel()
}
