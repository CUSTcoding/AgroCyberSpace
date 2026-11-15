import type { Reply, Slide, Speaker, SceneId, Challenge } from '../types'

export const go: Reply[] = [
  { icon: '👉', label: 'Seguir', say: '', action: 'next' },
  { icon: '🔁', label: 'Ouvir outra vez', say: '', action: 'repeat' },
]

export function line(
  id: string,
  scene: SceneId,
  speaker: Speaker,
  text: string,
  extra?: { replies?: Reply[]; challenge?: Challenge },
): Slide {
  return {
    id,
    scene,
    speaker,
    text,
    replies: extra?.replies ?? go,
    challenge: extra?.challenge,
  }
}
