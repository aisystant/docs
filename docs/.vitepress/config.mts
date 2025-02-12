import { defineConfig } from 'vitepress'
import path from 'path'
import { generateSidebar } from './utils/generateSidebar.js'

// Generate sidebars for different languages
const ruSidebar = generateSidebar(path.resolve(__dirname, '../ru'), 'ru')
// const enSidebar = generateSidebar(path.resolve(__dirname, '../en'), 'en')

export default defineConfig({
  title: "Aisystant Docs",
  description: " ",
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Examples', link: '/markdown-examples' }
    ],
    // Define multiple sidebars for language-specific routes
    sidebar: {
      '/ru/': ruSidebar,
//      '/en/': enSidebar,
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})