// 根据天气现象文字匹配一个 emoji 图标
export function weatherEmoji(text = '') {
  const t = String(text || '')
  if (/雷/.test(t)) return '⛈️'
  if (/雪|冰|霰/.test(t)) return '❄️'
  if (/雨|阵雨|毛毛雨/.test(t)) return '🌧️'
  if (/雾|霾|烟尘/.test(t)) return '🌫️'
  if (/阴/.test(t)) return '☁️'
  if (/云/.test(t)) return '⛅'
  if (/晴/.test(t)) return '☀️'
  return '🌡️'
}

// 把 YYYY-MM-DD 转成「今天 / 明天 / 周几」展示
export function dayLabel(dateStr, index) {
  if (!dateStr) return ''
  if (index === 0) return '今天'
  if (index === 1) return '明天'
  const d = new Date(dateStr + 'T00:00:00')
  if (Number.isNaN(d.getTime())) return dateStr
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return week[d.getDay()]
}
