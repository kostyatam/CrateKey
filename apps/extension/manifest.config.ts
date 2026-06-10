import { defineManifest } from '@crxjs/vite-plugin'

export default defineManifest({
  manifest_version: 3,
  name: 'CrateKey — DJ Key Detector',
  version: '0.1.0',
  description: 'Detects the musical key of tracks on streaming platforms.',
  action: {
    default_popup: 'src/popup/index.html',
  },
  background: {
    service_worker: 'src/background/index.ts',
    type: 'module',
  },
  permissions: ['storage', 'offscreen'],
  host_permissions: ['http://localhost:8000/*'],
  content_scripts: [
    {
      matches: ['https://www.beatport.com/*'],
      js: ['src/content/platforms/beatport.ts'],
    },
    {
      matches: ['https://www.traxsource.com/*'],
      js: ['src/content/platforms/traxsource.ts'],
    },
    {
      matches: ['https://soundcloud.com/*'],
      js: ['src/content/platforms/soundcloud.ts'],
    },
    {
      matches: ['https://*.bandcamp.com/*'],
      js: ['src/content/platforms/bandcamp.ts'],
    },
    {
      matches: ['https://www.youtube.com/*'],
      js: ['src/content/platforms/youtube.ts'],
    },
  ],
})
