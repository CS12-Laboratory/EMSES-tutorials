// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  site: 'https://cs12-laboratory.github.io',
  base: '/EMSES-tutorials',
  integrations: [
    starlight({
      title: 'EMSES tutorials',
      description:
        'MPIEMSES3D / EMSES を使い始めるためのチュートリアル集 — Tutorials for getting started with the MPIEMSES3D / EMSES electromagnetic particle code.',
      defaultLocale: 'root',
      locales: {
        root: { label: '日本語', lang: 'ja' },
        en: { label: 'English', lang: 'en' },
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/CS12-Laboratory/EMSES-tutorials',
        },
      ],
      sidebar: [
        {
          label: 'Getting started',
          translations: { ja: 'はじめに' },
          items: [
            {
              label: 'Quick Start',
              translations: { ja: '初回チュートリアル' },
              link: '/quick-start/',
            },
          ],
        },
        {
          label: 'Tips',
          translations: { ja: 'Tips' },
          autogenerate: { directory: 'tips' },
        },
        {
          label: 'References',
          translations: { ja: '参考資料' },
          items: [
            {
              label: 'MPIEMSES3D Parameters',
              link: 'https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md',
            },
            {
              label: 'MPIEMSES3D Customization',
              link: 'https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md',
            },
            {
              label: 'emout',
              link: 'https://github.com/Nkzono99/emout',
            },
          ],
        },
      ],
    }),
    mdx(),
  ],
});
