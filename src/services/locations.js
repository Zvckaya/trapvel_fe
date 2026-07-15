// src/services/locations.js
import api from './api'

export async function fetchLocations(params = {}) {
  const res = await api.get('/locations', { params })
  return res.data
}

export async function fetchLocation(locationId) {
  const res = await api.get(`/locations/${locationId}`)
  return res.data
}

export async function fetchWaterRocketIndex(locationId) {
  const res = await api.get(`/locations/${locationId}/water-rocket-index`)
  return res.data
}

export async function fetchWaterRocketExtremes(limit = 3) {
  const res = await api.get('/locations/water-rocket-extremes', {
    params: { limit },
  })
  return res.data
}

/**
 * Resolve backend internal `id` (integer) from local `contentId` (e.g. "126385").
 * Strategy:
 *  - call /locations?keyword=<contentId>&size=100 and try to match item.content_id/contentId/contentid
 *  - if not found, try fetching by numeric id as a fallback
 * Returns integer id or null if not found.
 */
export async function resolveLocationIdByContentId(contentId) {
  if (!contentId) return null
  const q = String(contentId)
  try {
    const data = await fetchLocations({ keyword: q, size: 100 })
    const items = data.items ?? data.data ?? data ?? []
    for (const item of items) {
      const itemContent =
        item.content_id ??
        item.contentId ??
        item.contentid ??
        (item.content && (item.content.content_id ?? item.content.contentId ?? item.content.contentid)) ??
        ''
      if (String(itemContent) === q) {
        return item.id ?? item.location_id ?? null
      }
    }

    // fallback: try treating contentId as numeric backend id
    try {
      const maybe = await fetchLocation(Number(q))
      if (maybe?.id) return maybe.id
    } catch (e) {
      // ignore — not found
    }
  } catch (err) {
    console.error('resolveLocationIdByContentId error', err)
  }
  return null
}
