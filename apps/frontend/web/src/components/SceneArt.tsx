import type { SceneId, Speaker } from '../types'
import { Icon } from './Icon'

const faces: Record<Speaker, string> = {
  astronaut: '🧑‍🚀',
  farmer: '👨‍🌾',
  amelia: '👵',
  manual: '📘',
  narrator: '✨',
  child: '👧',
}

export function SceneArt({ scene, speaker }: { scene: SceneId; speaker: Speaker }) {
  return (
    <div className={`scene scene-${scene}`} aria-hidden>
      <div className="stars" />
      <div className="scene-glow" />
      {scene === 'space' && <SpaceView />}
      {scene === 'ship' && <ShipView />}
      {scene === 'hologram' && <HoloView />}
      {scene === 'village' && <VillageView />}
      {scene === 'farm' && <FarmView />}
      {scene === 'dry' && <FarmView dry />}
      {scene === 'heat' && <FarmView heat />}
      {scene === 'rain' && <FarmView rain />}
      {scene === 'soil' && <SoilView />}
      {scene === 'lab' && <LabView />}
      {scene === 'academy' && <AcademyView />}
      {scene === 'storm' && <StormView />}
      {scene === 'harvest' && <HarvestView />}
      {scene === 'night' && <NightView />}
      {scene === 'council' && <VillageView council />}
      <div className={`hero-face face-${speaker}`}><Icon name={faces[speaker]} /></div>
    </div>
  )
}

function SpaceView() {
  return (
    <div className="art space-art">
      <div className="earth" />
      <div className="ship-body" />
    </div>
  )
}

function ShipView() {
  return (
    <div className="art ship-art">
      <div className="console" />
      <div className="window-earth" />
    </div>
  )
}

function HoloView() {
  return (
    <div className="art holo-art">
      <div className="holo-globe" />
      <div className="holo-rings" />
    </div>
  )
}

function VillageView({ council }: { council?: boolean }) {
  return (
    <div className={`art village-art ${council ? 'council' : ''}`}>
      <div className="hut h1" />
      <div className="hut h2" />
      <div className="tree"><Icon name="🌳" /></div>
      <div className="people">
        <Icon name="👨‍🌾" />
        <Icon name="👵" />
        <Icon name="👧" />
      </div>
    </div>
  )
}

function FarmView({ dry, heat, rain }: { dry?: boolean; heat?: boolean; rain?: boolean }) {
  return (
    <div className={`art farm-art ${dry ? 'dry' : ''} ${heat ? 'heat' : ''} ${rain ? 'rainy' : ''}`}>
      <div className="field" />
      <div className="maize">
        <Icon name="🌽" />
        <Icon name="🌽" />
        <Icon name="🌽" />
        <Icon name="🌽" />
      </div>
      {rain && <div className="rain-drops" />}
      {heat && <div className="sun-ball" />}
    </div>
  )
}

function SoilView() {
  return (
    <div className="art soil-art">
      <div className="layer top" />
      <div className="layer mid" />
      <div className="layer deep" />
      <div className="root"><Icon name="🌱" /></div>
    </div>
  )
}

function LabView() {
  return (
    <div className="art lab-art">
      <div className="panel p1" />
      <div className="panel p2" />
      <div className="panel p3" />
    </div>
  )
}

function AcademyView() {
  return (
    <div className="art academy-art">
      <div className="portal"><Icon name="🌽" /></div>
      <div className="portal"><Icon name="🫘" /></div>
      <div className="portal"><Icon name="🌾" /></div>
      <div className="portal"><Icon name="🥜" /></div>
    </div>
  )
}

function StormView() {
  return (
    <div className="art storm-art">
      <div className="bolt" />
      <div className="field dark" />
    </div>
  )
}

function HarvestView() {
  return (
    <div className="art harvest-art">
      <div className="basket"><Icon name="🧺" /></div>
      <div className="maize">
        <Icon name="🌽" />
        <Icon name="🫘" />
        <Icon name="🌾" />
      </div>
    </div>
  )
}

function NightView() {
  return (
    <div className="art night-art">
      <div className="moon" />
      <div className="ship-away"><Icon name="🚀" /></div>
    </div>
  )
}
