// 生活信息：浏览器定位 + 拉取天气
import { ref } from 'vue'
import { request } from '../api/request'

// 定位失败时兜底城市：成都（经度, 纬度）
const DEFAULT_LNG = 104.06
const DEFAULT_LAT = 30.57

export function useLife() {
  const weather = ref(null)
  const loadingWeather = ref(false)
  const locationNote = ref('')

  // 浏览器定位；拒绝 / 超时 / 不支持时回退默认城市
  function getPosition() {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({ lng: DEFAULT_LNG, lat: DEFAULT_LAT, fallback: true })
        return
      }
      navigator.geolocation.getCurrentPosition(
        (pos) =>
          resolve({ lng: pos.coords.longitude, lat: pos.coords.latitude, fallback: false }),
        () => resolve({ lng: DEFAULT_LNG, lat: DEFAULT_LAT, fallback: true }),
        { timeout: 8000, maximumAge: 600000 }
      )
    })
  }

  async function loadWeather() {
    loadingWeather.value = true
    const { lng, lat, fallback } = await getPosition()
    locationNote.value = fallback ? '未能获取定位，已按默认城市展示' : ''
    const { data } = await request(`/api/life/weather/?lng=${lng}&lat=${lat}`)
    if (data?.code === 200) weather.value = data.data
    loadingWeather.value = false
  }

  return {
    weather,
    loadingWeather,
    locationNote,
    loadWeather,
  }
}
