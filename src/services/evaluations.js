// src/services/evaluations.js
import api from './api'

export async function fetchPreVisitEvaluations(locationId, params = {}) {
  const res = await api.get(`/locations/${locationId}/pre-visit-evaluations`, { params })
  return res.data
}

export async function createPreVisitEvaluation(locationId, body) {
  const res = await api.post(`/locations/${locationId}/pre-visit-evaluations`, body)
  return res.data
}

export async function fetchPostVisitEvaluations(locationId, params = {}) {
  const res = await api.get(`/locations/${locationId}/post-visit-evaluations`, { params })
  return res.data
}

export async function createPostVisitEvaluation(locationId, body) {
  const res = await api.post(`/locations/${locationId}/post-visit-evaluations`, body)
  return res.data
}