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
  // Read directory contents (files and subdirectories)
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  const items = []

  for (const entry of entries) {
    // If the entry is a directory, process it recursively
    if (entry.isDirectory()) {
      const subdir = path.join(dir, entry.name)
      const subItems = generateSidebar(subdir, path.join(base, entry.name))

      if (subItems.length) {
        // Attempt to retrieve the section title from an index.md file if it exists
        let title = entry.name
        const indexPath = path.join(subdir, 'index.md')
        if (fs.existsSync(indexPath)) {
          try {
            const content = fs.readFileSync(indexPath, 'utf-8')
            const { data } = matter(content)
            title = data.title || title
          } catch (error) {
            console.warn(`Error reading file ${indexPath}: ${error.message}`)
          }
        }

        // For directories, create a collapsible group that is closed by default.
        items.push({
          text: title,
          items: subItems,
          collapsed: true, // group is collapsed by default
          order: subItems[0].order || 0 // Optionally set group order based on the first child
        })
      }
    }
    // If the entry is a Markdown file
    else if (entry.isFile() && entry.name.endsWith('.md')) {
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

      // Create the link: use base path for index.md, otherwise remove .md extension
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

  // Sort items based on the order field
  items.sort((a, b) => (a.order || 0) - (b.order || 0))

  // Remove the temporary order property before returning the items
  return items.map(({ order, ...rest }) => rest)
}
