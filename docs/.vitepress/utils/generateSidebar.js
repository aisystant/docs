import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

/**
 * Recursively generates sidebar items for a section directory and sorts pages based on frontmatter order.
 *
 * @param {string} dir - Absolute path to the section directory.
 * @param {string} base - Base URL for the section directory.
 * @returns {Array} Array of sidebar items.
 */
function generateSectionSidebar(dir, base = '') {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  const items = []

  for (const entry of entries) {
    if (entry.isDirectory()) {
      // Skip assets and other non-content directories
      if (entry.name === 'assets' || entry.name.startsWith('.')) continue

      const subdir = path.join(dir, entry.name)
      const subItems = generateSectionSidebar(subdir, path.join(base, entry.name))
      let title = entry.name
      let order = 0
      const indexPath = path.join(subdir, 'index.md')
      if (fs.existsSync(indexPath)) {
        try {
          const content = fs.readFileSync(indexPath, 'utf-8')
          const { data } = matter(content)
          title = data.title || title
          order = data.order || 0
        } catch (error) {
          console.warn(`Error reading ${indexPath}: ${error.message}`)
        }
      }
      if (subItems.length > 0) {
        items.push({
          text: title,
          collapsed: true,
          items: subItems,
          order
        })
      } else {
        const link = '/' + path.join(base, entry.name, 'index').replace(/\\/g, '/')
        items.push({
          text: title,
          link: link,
          order
        })
      }
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      if (entry.name === 'index.md') continue
      const filePath = path.join(dir, entry.name)
      let fileContent, data, order = 0
      try {
        fileContent = fs.readFileSync(filePath, 'utf-8')
        const parsed = matter(fileContent)
        data = parsed.data
        order = data.order || 0
      } catch (error) {
        console.warn(`Error reading file ${filePath}: ${error.message}`)
        continue
      }
      const link = path.join(base, entry.name.replace(/\.md$/, ''))
      items.push({
        text: data.title || entry.name.replace(/\.md$/, ''),
        link: '/' + link.replace(/\\/g, '/'),
        order
      })
    }
  }

  items.sort((a, b) => {
    if (a.order !== b.order) return a.order - b.order
    return a.text.localeCompare(b.text)
  })

  return items.map(({ order, ...rest }) => rest)
}

/**
 * Generates a course sidebar with a single group header (course title)
 * and collapsible items for each section, including course-level files.
 *
 * @param {string} courseDir - Absolute path to the course directory.
 * @param {string} base - Base URL for the course directory.
 * @returns {Array} Array containing a single sidebar group.
 */
export function generateCourseSidebar(courseDir, base = '') {
  let courseTitle = path.basename(courseDir)
  const courseIndex = path.join(courseDir, 'index.md')
  if (fs.existsSync(courseIndex)) {
    try {
      const content = fs.readFileSync(courseIndex, 'utf-8')
      const { data } = matter(content)
      courseTitle = data.title || courseTitle
    } catch (error) {
      console.warn(`Error reading course index ${courseIndex}: ${error.message}`)
    }
  }

  const courseItems = []
  const entries = fs.readdirSync(courseDir, { withFileTypes: true })

  for (const entry of entries) {
    if (entry.isFile() && entry.name.endsWith('.md') && entry.name !== 'index.md') {
      const filePath = path.join(courseDir, entry.name)
      let fileContent, data
      try {
        fileContent = fs.readFileSync(filePath, 'utf-8')
        const parsed = matter(fileContent)
        data = parsed.data
      } catch (error) {
        console.warn(`Error reading file ${filePath}: ${error.message}`)
        continue
      }
      const link = path.join(base, entry.name.replace(/\.md$/, ''))
      courseItems.push({
        text: data.title || entry.name.replace(/\.md$/, ''),
        order: data.order || 0,
        link: '/' + link.replace(/\\/g, '/')
      })
    }
  }

  for (const entry of entries) {
    if (entry.isDirectory()) {
      // Skip assets and other non-content directories
      if (entry.name === 'assets' || entry.name.startsWith('.')) continue

      const sectionDir = path.join(courseDir, entry.name)
      let sectionTitle = entry.name
      let order = 0
      const sectionIndex = path.join(sectionDir, 'index.md')
      if (fs.existsSync(sectionIndex)) {
        try {
          const content = fs.readFileSync(sectionIndex, 'utf-8')
          const { data } = matter(content)
          sectionTitle = data.title || sectionTitle
          order = data.order || 0
        } catch (error) {
          console.warn(`Error reading section index ${sectionIndex}: ${error.message}`)
        }
      }
      const items = generateSectionSidebar(sectionDir, path.join(base, entry.name))
      if (items.length > 0) {
        courseItems.push({
          text: sectionTitle,
          collapsed: true,
          items,
          order
        })
      } else {
        const link = '/' + path.join(base, entry.name, 'index').replace(/\\/g, '/')
        courseItems.push({
          text: sectionTitle,
          link,
          order
        })
      }
    }
  }

  console.error('courseItems', courseItems)

  courseItems.sort((a, b) => {
    if ((a.order || 0) !== (b.order || 0)) return (a.order || 0) - (b.order || 0)
    return (a.text || '').localeCompare(b.text || '')
  })

  const cleanedItems = courseItems.map(({ order, ...rest }) => rest)

  return [
    {
      text: courseTitle,
      collapsed: false,
      items: cleanedItems
    }
  ]
}
