import rawTouristData from './광주_전라권_관광지.json'

const sourceItems = rawTouristData.items ?? []

const buildImageUrl = (value) => {
  if (!value) return ''
  return value
}

const normalizePlace = (item) => {
  return {
    id: item.contentid,
    name: item.title,
    address: [item.addr1, item.addr2].filter(Boolean).join(' ').trim(),
    region: rawTouristData.region,
    contentType: rawTouristData.contentType,
    contentTypeId: rawTouristData.contentTypeId,
    mainImage: buildImageUrl(item.firstimage),
    thumbnailImage: buildImageUrl(item.firstimage2 || item.firstimage),
    mapx: Number(item.mapx),
    mapy: Number(item.mapy),
    tel: item.tel,
    zipcode: item.zipcode,
    raw: item,
  }
}

export const touristPlaces = sourceItems.map(normalizePlace)

export const getTouristPlaceById = (id) => {
  const targetId = String(id)
  return touristPlaces.find((place) => String(place.id) === targetId) ?? null
}

export const getTopTouristPlaces = (count = 3) => {
  return touristPlaces.slice(0, count)
}