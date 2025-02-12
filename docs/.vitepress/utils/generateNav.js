import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

/**
 * Dynamically generates nav items by scanning the courses directory.
 *
 * @param {string} coursesDir - Absolute path to the directory containing course folders.
 * @param {string} base - Base URL path for the courses (e.g., '/ru').
 * @returns {Array} Array of navigation item objects.
 */
export function generateCourseNav(coursesDir, base = '/ru') {
  const entries = fs.readdirSync(coursesDir, { withFileTypes: true })
  const navItems = []

  entries.forEach(entry => {
    if (entry.isDirectory()) {
      const coursePath = path.join(coursesDir, entry.name)
      let courseTitle = entry.name // default title is the folder name
      let courseOrder = 0

      // Check for an index.md file in the course folder to retrieve title and order
      const indexFile = path.join(coursePath, 'index.md')
      if (fs.existsSync(indexFile)) {
        try {
          const fileContent = fs.readFileSync(indexFile, 'utf-8')
          const { data } = matter(fileContent)
          if (data.title) {
            courseTitle = data.title
          }
          if (data.order) {
            courseOrder = data.order
          }
        } catch (error) {
          console.warn(`Error reading ${indexFile}: ${error.message}`)
        }
      }

      navItems.push({
        text: courseTitle,
        link: `${base}/${entry.name}/`,
        order: courseOrder
      })
    }
  })

  // Sort nav items by order
  navItems.sort((a, b) => (a.order || 0) - (b.order || 0))

  // Remove the order property before returning
  return navItems.map(({ order, ...rest }) => rest)
}
