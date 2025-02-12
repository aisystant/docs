import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

/**
 * Recursively generates a sidebar structure based on markdown files in a given directory.
 *
 * @param {string} dir - Absolute path to the directory to process.
 * @param {string} base - Base URL path for generated links.
 * @returns {Array} Array of sidebar item objects.
 */
export function generateSidebar(dir, base = '') {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  const items = []

  for (const entry of entries) {
    if (entry.isDirectory()) {
      const subdir = path.join(dir, entry.name)
      let subItems = generateSidebar(subdir, path.join(base, entry.name))

      let title = entry.name
      let groupOrder = undefined

      // Check for an index.md file in the directory to use as the group header
      const indexPath = path.join(subdir, 'index.md')
      if (fs.existsSync(indexPath)) {
        try {
          const content = fs.readFileSync(indexPath, 'utf-8')
          const { data } = matter(content)
          title = data.title || title
          groupOrder = data.order ?? 0
          // Previously we generated a groupLink here.
          // For toggle behavior only, do not assign a link property.
          // const groupLink = '/' + path.join(base, entry.name, 'index').replace(/\\/g, '/')
        } catch (error) {
          console.warn(`Error reading file ${indexPath}: ${error.message}`)
        }
        // If an index.md file was processed, remove it from subItems to avoid duplicate entries.
        subItems = subItems.filter(item => !item.link.endsWith(`/${entry.name}/`)) // Adjust filtering as needed.
      } else {
        groupOrder = subItems.length > 0 ? (subItems[0].order || 0) : 0
      }

      if (subItems.length) {
        // Create the group item without a link property.
        const groupItem = {
          text: title,
          collapsed: true, // group is collapsed by default
          order: groupOrder,
          items: subItems
        }
        items.push(groupItem)
      }
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      const filePath = path.join(dir, entry.name)
      let fileContent, data

      try {
        fileContent = fs.readFileSync(filePath, 'utf-8')
        const parsed = matter(fileContent)
        data = parsed.data
      } catch (error) {
        console.warn(`Error processing file ${filePath}: ${error.message}`)
        continue
      }

      let link = path.join(base, entry.name.replace(/\.md$/, ''))
      if (entry.name === 'index.md') {
        link = base || '/'
      }

      items.push({
        text: data.title || entry.name.replace(/\.md$/, ''),
        link: '/' + link.replace(/\\/g, '/'),
        order: data.order || 0
      })
    }
  }

  items.sort((a, b) => (a.order || 0) - (b.order || 0))
  return items.map(({ order, ...rest }) => rest)
}