// 富文本工具：从编辑器 HTML 提取纯文本，用于列表摘要展示

// HTML -> 纯文本（去掉标签，合并空白）
export function htmlToText(html) {
  if (!html) return ''
  const div = document.createElement('div')
  div.innerHTML = html
  return (div.textContent || '').replace(/\s+/g, ' ').trim()
}

// 取摘要：纯文本截断到指定字数，超出加省略号
export function excerpt(html, len = 80) {
  const text = htmlToText(html)
  return text.length > len ? `${text.slice(0, len)}…` : text
}
