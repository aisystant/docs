import { defineConfig } from 'vitepress'
import path from 'path'
import { generateSidebar } from './utils/generateSidebar.js'
import { generateCourseNav } from './utils/generateNav.js'

// Define the base directory for your courses (adjust as needed)
const ruDir = path.resolve(__dirname, '../ru')

// Dynamically generate navigation items for each course in the /ru folder
const courseNav = generateCourseNav(ruDir, '/ru')

// Dynamically generate a sidebar for each course by scanning its subdirectories
const sidebar = {}
courseNav.forEach(course => {
  // Extract the course folder name from the course link (e.g. 'course1' from '/ru/course1/')
  const courseName = course.link.replace(/^\/|\/$/g, '').split('/')[1]
  sidebar[`/ru/${courseName}/`] = generateSidebar(path.join(ruDir, courseName), `ru/${courseName}`)
})

export default defineConfig({
  title: "Aisystant Docs",
  description: "Documentation for Aisystant",
  themeConfig: {
    // Use dynamically generated navigation items for the courses
    nav: [
      { text: 'Home', link: '/' },
      ...courseNav,
      { text: 'Examples', link: '/markdown-examples' }
    ],
    // Map each course route to its generated sidebar
    sidebar,
    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})