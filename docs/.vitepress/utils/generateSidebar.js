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
    // If the entry is a directory, process it recursively as a group (section)
    if (entry.isDirectory()) {
      const subdir = path.join(dir, entry.name)
      let subItems = generateSidebar(subdir, path.join(base, entry.name))

      // Defaults for the group header
      let title = entry.name
      let groupOrder = undefined
      let groupLink = undefined

      // Check for an index.md file in the directory to use as the group header
      const indexPath = path.join(subdir, 'index.md')
      if (fs.existsSync(indexPath)) {
        try {
          const content = fs.readFileSync(indexPath, 'utf-8')
          const { data } = matter(content)
          title = data.title || title
          groupOrder = data.order ?? 0
          // Create a link for the group header based on the index.md file
          groupLink = '/' + path.join(base, entry.name, 'index').replace(/\\/g, '/')
        } catch (error) {
          console.warn(`Error reading file ${indexPath}: ${error.message}`)
        }
        // Remove the index.md item from subItems to avoid duplicate entries
        subItems = subItems.filter(item => item.link !== groupLink)
      } else {
        groupOrder = subItems.length > 0 ? (subItems[0].order || 0) : 0
      }

      if (subItems.length) {
        const groupItem = {
          text: title,
          collapsed: true, // Group is collapsed by default
          order: groupOrder,
          items: subItems
        }

        // Optionally add a link to the group header if index.md was found
        if (groupLink) {
          groupItem.link = groupLink
        }

        items.push(groupItem)
      }
    }
    // If the entry is a Markdown file, process it as a regular page
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

      // Create the link: for index.md, use the base path; otherwise remove the .md extension
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