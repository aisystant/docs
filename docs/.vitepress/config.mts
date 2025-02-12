import { defineConfig } from 'vitepress'
import path from 'path'
import { generateSidebar } from './utils/generateSidebar.js'
import { generateCourseNav } from './utils/generateNav.js'

// Define the base directory for the Russian content
const ruDir = path.resolve(__dirname, '../ru')

// Dynamically generate navigation items for courses in the /ru directory
const ruCourseNav = generateCourseNav(ruDir, '/ru')

// Dynamically generate a sidebar for each course in /ru
const ruSidebar = {}
ruCourseNav.forEach(course => {
  // Extract the course folder name from course.link (e.g., "course1" from "/ru/course1/")
  const parts = course.link.split('/').filter(Boolean) // remove empty strings
  const courseName = parts[1]  // parts[0] is "ru", parts[1] is the course name
  ruSidebar[`/ru/${courseName}/`] = generateSidebar(
    path.join(ruDir, courseName),
    `ru/${courseName}`
  )
})

export default defineConfig({
  title: "Aisystant Docs",
  description: "Documentation for Aisystant",
  // Top-level locales configuration: keys are base paths for each locale.
  locales: {
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      themeConfig: {
        // Currently empty for English; can be populated when English content is available.
        nav: [],
        sidebar: {},
        socialLinks: [
          { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
        ]
      }
    },
    ru: {
      label: 'Русский',
      lang: 'ru-RU',
      link: '/ru/',
      themeConfig: {
        nav: ruCourseNav,      // Dynamically generated navigation for Russian courses
        sidebar: ruSidebar,      // Dynamically generated sidebar for Russian courses
        socialLinks: [
          { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
        ]
      },
    },
  },
})