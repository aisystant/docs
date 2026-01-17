import { defineConfig } from 'vitepress'
import path from 'path'
import { generateCourseSidebar } from './utils/generateSidebar.js'
import { generateCourseNav } from './utils/generateNav.js'
import footnote from 'markdown-it-footnote' // Import the footnotes plugin

// Russian version configuration
const ruDir = path.resolve(__dirname, '../ru')
const ruCourseNav = generateCourseNav(ruDir, '/ru')
const ruSidebar = {}
ruCourseNav.forEach(course => {
  // Extract the course folder name from course.link (e.g., "course1" from "/ru/course1/")
  const parts = course.link.split('/').filter(Boolean)
  const courseName = parts[1]  // parts[0] is "ru", parts[1] is the course name
  ruSidebar[`/ru/${courseName}/`] = generateCourseSidebar(
    path.join(ruDir, courseName),
    `ru/${courseName}`
  )
})

// English version configuration
const enDir = path.resolve(__dirname, '../en')
const enCourseNav = generateCourseNav(enDir, '/en')
const enSidebar = {}
enCourseNav.forEach(course => {
  // Extract the course folder name from course.link (e.g., "course1" from "/en/course1/")
  const parts = course.link.split('/').filter(Boolean)
  const courseName = parts[1]  // parts[0] is "en", parts[1] is the course name
  enSidebar[`/en/${courseName}/`] = generateCourseSidebar(
    path.join(enDir, courseName),
    `en/${courseName}`
  )
})

export default defineConfig({
  title: "Aisystant Docs",
  description: "Documentation for Aisystant",
  cleanUrls: false,
  markdown: {
    config: (md) => {
      md.use(footnote) // Enable footnotes support
    }
  },
  locales: {
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      themeConfig: {
        nav: enCourseNav,      // Dynamically generated navigation for English courses
        sidebar: enSidebar,    // Dynamically generated sidebar with collapsible section items
        socialLinks: [
          { icon: 'github', link: 'https://github.com/aisystant/docs' }
        ]
      }
    },
    ru: {
      label: 'Русский',
      lang: 'ru-RU',
      link: '/ru/',
      themeConfig: {
        nav: ruCourseNav,      // Dynamically generated navigation for Russian courses
        sidebar: ruSidebar,    // Dynamically generated sidebar with collapsible section items
        socialLinks: [
          { icon: 'github', link: 'https://github.com/aisystant/docs' }
        ]
      }
    }
  },
  head: [
    [
      'script',
      {},
      `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
      })(window,document,'script','dataLayer','GTM-K7MKK9Q5');`
    ]
  ]
})
