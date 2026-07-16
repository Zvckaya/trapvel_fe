<template>
  <div class="tourist-detail-page">
    <section v-if="place" class="page-header">
      <div class="page-header-left">
        <p class="page-kicker">관광객 리뷰</p>
        <div class="title-row">
          <span class="title-accent" />
          <div>
            <h1 class="page-title">{{ place.title }}</h1>
            <p class="page-address">{{ place.addr1 || '주소 정보 없음' }}</p>
          </div>
        </div>
      </div>

      <button class="back-link" @click="goBack" aria-label="목록으로">
        <i class="pi pi-arrow-left back-icon" aria-hidden="true"></i>
        <span class="back-text">목록으로</span>
      </button>
    </section>

    <Card v-if="loadingPlace" class="surface-card">
      <template #content>
        <div class="status-box">관광지 정보를 불러오는 중입니다.</div>
      </template>
    </Card>

    <Card v-else-if="errorMessage" class="surface-card">
      <template #content>
        <div class="status-box error-text">{{ errorMessage }}</div>
      </template>
    </Card>

    <template v-else-if="place">
      <!-- Hero: image and metric -->
      <Card class="surface-card hero-card">
        <template #content>
          <div class="hero-grid">
            <div class="hero-image-wrap">
              <img
                :src="place.firstimage || place.firstimage2 || fallbackImage"
                :alt="place.title"
                class="hero-image"
              />
            </div>

            <div class="hero-panel">
              <div class="metric-lead">
                <div class="metric-row">
                  <div class="metric-text">
                    <p class="metric-kicker">물로켓 지수</p>
                    <h2 class="metric-value">{{ formattedWaterRocketScore }}</h2>
                    <p class="metric-sub">기대와 실제 만족도의 차이를 한눈에 보여주는 지표입니다.</p>
                  </div>

                  <div class="bar-wrap">
                    <div class="bar-bg">
                      <div class="bar-fill" :style="{ width: fillPercent + '%', background: barColor, right: isNegative ? 0 : 'auto', left: isNegative ? 'auto' : 0 }" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="metric-grid">
                <div class="metric-card">
                  <span class="metric-label">물로켓 지수</span>
                  <strong class="metric-number">{{ formattedWaterRocketScore }}</strong>
                </div>
                <div class="metric-card">
                  <span class="metric-label">방문 전 평균</span>
                  <strong class="metric-number">{{ formattedPreVisitAvg }}</strong>
                </div>
                <div class="metric-card">
                  <span class="metric-label">방문 후 평균</span>
                  <strong class="metric-number">{{ formattedPostVisitAvg }}</strong>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Rating block -->
      <Card class="surface-card rating-container">
        <template #content>
          <div class="rating-row">
            <div class="rating-card">
              <div class="rating-kicker">관광 전</div>
              <div class="rating-options" role="radiogroup" aria-label="관광 전 평점">
                <button v-for="n in 5" :key="`before-${n}`" type="button" class="rating-option" :class="{ active: form.beforeScore === n }" @click="setBeforeScore(n)">{{ n }}</button>
              </div>
            </div>

            <div class="rating-card">
              <div class="rating-kicker">관광 후</div>
              <div class="rating-options" role="radiogroup" aria-label="관광 후 평점">
                <button v-for="n in 5" :key="`after-${n}`" type="button" class="rating-option" :class="{ active: form.afterScore === n }" @click="setAfterScore(n)">{{ n }}</button>
              </div>
            </div>
          </div>

          <div class="rating-submit-row">
            <button type="button" class="register-btn native-register" :disabled="submitting" @click="submitRating">평가하기</button>
          </div>
        </template>
      </Card>

      <!-- Comments -->
      <section class="comments-section">
        <div class="comments-header">
          <h2 class="comments-title">댓글</h2>
          <Tag :value="`${comments.length}개`" severity="info" />
        </div>

        <Card class="surface-card comments-card">
          <template #content>
            <div class="comment-compose">
              <div class="comment-credentials">
                <InputText
                  id="comment-author"
                  v-model="form.author"
                  placeholder="닉네임"
                  maxlength="50"
                  class="comment-author-input"
                  @keydown.enter="submitComment"
                />
                <InputText
                  id="comment-password"
                  v-model="passwordInput"
                  type="password"
                  placeholder="비밀번호 숫자 4자리"
                  maxlength="4"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  class="comment-password-input"
                  @input="onPasswordInput"
                  @keydown.enter="submitComment"
                />
              </div>

              <div class="comment-editor">
                <Textarea
                  v-model="form.comment"
                  placeholder="타인의 권리를 침해하거나 명예를 훼손하는 댓글은 운영원칙 및 관련 법률에 따라 제재를 받을 수 있습니다."
                  class="comment-input"
                  rows="4"
                  autoResize
                />
                <div class="comment-action">
                  <button type="button" class="comment-submit native-comment" :disabled="submitting" @click="submitComment">등록</button>
                </div>
              </div>
            </div>

            <div v-if="loadingComments" class="status-box">댓글을 불러오는 중입니다.</div>

            <div v-else-if="comments.length > 0" class="comment-list">
              <article v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-bubble">
                  <p class="comment-text">{{ comment.content }}</p>
                </div>
                <div class="comment-meta">
                  <span class="comment-author">{{ comment.author || '익명' }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                  <Button text icon="pi pi-trash" class="p-button-text comment-delete" @click="confirmDelete(comment)" />
                </div>
              </article>
            </div>

            <div v-else class="status-box">등록된 댓글이 없습니다.</div>
          </template>
        </Card>
      </section>
    </template>

  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'

import { fetchLocation, fetchWaterRocketIndex, resolveLocationIdByContentId } from '@/services/locations'
import { fetchComments, createComment as createCommentApi, deleteComment as deleteCommentApi } from '@/services/comment'
import {
  createPostVisitEvaluation,
  createPreVisitEvaluation,
  fetchPostVisitEvaluations,
  fetchPreVisitEvaluations,
} from '@/services/evaluations'

const route = useRoute()
const router = useRouter()

const fallbackImage = '/images/placeholder-place.jpg'
const backendId = ref(null)
const place = ref(null)
const comments = ref([])
const loadingPlace = ref(false)
const loadingComments = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const waterRocketScore = ref(null)
const preVisitAvg = ref(null)
const postVisitAvg = ref(null)

const form = reactive({ beforeScore: 0, afterScore: 0, author: '', comment: '' })

const passwordInput = ref('')

const formatValue = (value) => {
  const num = Number(value)
  if (!Number.isFinite(num)) return '-'
  return Number.isInteger(num) ? `${num}` : num.toFixed(1)
}

const formattedWaterRocketScore = computed(() => formatValue(waterRocketScore.value))
const formattedPreVisitAvg = computed(() => formatValue(preVisitAvg.value))
const formattedPostVisitAvg = computed(() => formatValue(postVisitAvg.value))

/* bar helpers */
const fillPercent = computed(() => {
  const v = Number(waterRocketScore.value) || 0
  const abs = Math.min(Math.abs(v), 5)
  return Math.round((abs / 5) * 100)
})
const isNegative = computed(() => Number(waterRocketScore.value) < 0)
const barColor = computed(() => (isNegative.value ? '#ff3b3b' : '#1f6feb'))

const previewScore = computed(() => {
  const b = Number(form.beforeScore) || 0
  const a = Number(form.afterScore) || 0
  return a - b
})
const previewScoreFormatted = computed(() => (Number.isFinite(previewScore.value) ? previewScore.value.toFixed(1) : '-'))

const averageBy = (items, key) => {
  if (!Array.isArray(items) || items.length === 0) return null
  const values = items.map((item) => Number(item?.[key])).filter((v) => Number.isFinite(v))
  if (values.length === 0) return null
  return values.reduce((s, v) => s + v, 0) / values.length
}

const resolveBackendId = async () => {
  const rawId = String(route.params.id)
  try {
    await fetchLocation(rawId)
    return rawId
  } catch {
    return resolveLocationIdByContentId(rawId)
  }
}

const loadPlace = async () => {
  if (!backendId.value) return
  loadingPlace.value = true
  errorMessage.value = ''
  try {
    place.value = await fetchLocation(backendId.value)
  } catch (error) {
    console.error('loadPlace error', error)
    place.value = null
    errorMessage.value = '관광지 상세 정보를 불러오지 못했습니다.'
  } finally {
    loadingPlace.value = false
  }
}

const loadWaterRocketIndex = async () => {
  if (!backendId.value) return
  try {
    const data = await fetchWaterRocketIndex(backendId.value)
    waterRocketScore.value = Number(data?.water_rocket_index ?? 0)
    preVisitAvg.value = data?.pre_visit_avg ?? null
    postVisitAvg.value = data?.post_visit_avg ?? null
  } catch (error) {
    console.error('loadWaterRocketIndex error', error)
    waterRocketScore.value = null
  }
}

const loadEvaluationAverages = async () => {
  if (!backendId.value) return
  try {
    const [preList, postList] = await Promise.all([fetchPreVisitEvaluations(backendId.value), fetchPostVisitEvaluations(backendId.value)])
    preVisitAvg.value = averageBy(preList, 'expectation_score')
    postVisitAvg.value = averageBy(postList, 'satisfaction_score')
  } catch (error) {
    console.error('loadEvaluationAverages error', error)
  }
}

const loadComments = async () => {
  if (!backendId.value) return
  loadingComments.value = true
  try {
    const data = await fetchComments(backendId.value)
    comments.value = data.items ?? data.data ?? data ?? []
  } catch (error) {
    console.error('loadComments error', error)
    comments.value = []
  } finally {
    loadingComments.value = false
  }
}

const loadAll = async () => {
  backendId.value = await resolveBackendId()
  if (!backendId.value) {
    place.value = null
    comments.value = []
    waterRocketScore.value = null
    preVisitAvg.value = null
    postVisitAvg.value = null
    errorMessage.value = '관광지 식별자를 확인할 수 없습니다.'
    return
  }
  await Promise.all([loadPlace(), loadComments(), loadWaterRocketIndex(), loadEvaluationAverages()])
}

// rating selection
const setBeforeScore = (n) => { if (n >= 1 && n <= 5) form.beforeScore = n }
const setAfterScore = (n) => { if (n >= 1 && n <= 5) form.afterScore = n }

// submit rating
const submitRating = async () => {
  if (!(form.beforeScore >= 1 && form.beforeScore <= 5)) { alert('관광 전 평점을 1~5 사이에서 선택해주세요.'); return }
  if (!(form.afterScore >= 1 && form.afterScore <= 5)) { alert('관광 후 평점을 1~5 사이에서 선택해주세요.'); return }
  if (!backendId.value) { alert('식별자 오류입니다.'); return }
  submitting.value = true
  try {
    await createPreVisitEvaluation(backendId.value, { author: '익명', expectation_score: Number(form.beforeScore) })
    await createPostVisitEvaluation(backendId.value, { author: '익명', satisfaction_score: Number(form.afterScore) })
    form.beforeScore = 0; form.afterScore = 0
    await Promise.all([loadWaterRocketIndex(), loadEvaluationAverages()])
    alert('평가가 등록되었습니다.')
  } catch (error) {
    console.error('submitRating error', error)
    alert(error.response?.data?.detail || '평가 등록에 실패했습니다.')
  } finally { submitting.value = false }
}

// comment flow
const onPasswordInput = (event) => {
  passwordInput.value = event.target.value.replace(/\D/g, '').slice(0, 4)
}

const submitComment = async () => {
  const author = form.author.trim()
  const content = form.comment.trim()
  if (!author) { alert('닉네임을 입력해주세요.'); return }
  if (!content) { alert('댓글을 입력해주세요.'); return }
  if (!/^\d{4}$/.test(String(passwordInput.value))) { alert('비밀번호는 숫자 4자리여야 합니다.'); return }
  if (!backendId.value) { alert('식별자 오류입니다.'); return }
  submitting.value = true
  try {
    await createCommentApi(backendId.value, { author, content, password: String(passwordInput.value) })
    form.author = ''
    form.comment = ''
    passwordInput.value = ''
    await Promise.all([loadComments(), loadWaterRocketIndex(), loadEvaluationAverages()])
    alert('댓글이 등록되었습니다.')
  } catch (error) {
    console.error('submitComment error', error)
    alert(error.response?.data?.detail || '댓글 등록에 실패했습니다.')
  } finally { submitting.value = false }
}

const confirmDelete = async (comment) => {
  const password = prompt('댓글 삭제 비밀번호 4자리를 입력해주세요.')
  if (!password) return
  if (!/^\d{4}$/.test(String(password))) { alert('비밀번호는 숫자 4자리여야 합니다.'); return }
  try { await deleteCommentApi(comment.id, password); await Promise.all([loadComments(), loadWaterRocketIndex(), loadEvaluationAverages()]) } catch (error) { console.error('deleteComment error', error); alert(error.response?.data?.detail || '삭제에 실패했습니다.') }
}

const formatDate = (iso) => { if (!iso) return ''; return iso.slice(0, 10) }
const goBack = () => { router.push('/tourists') }

onMounted(() => { loadAll() })
watch(() => route.params.id, () => { loadAll() })
</script>

<style scoped>
.tourist-detail-page{--color-primary:#1f6feb;--color-primary-600:#0f4fe8;--color-muted:#6b7280;--bg:#f4f8ff;--card-bg:#ffffff;--accent-blue:#1f6feb;--bubble-bg:#eaf6ff;max-width:920px;margin:24px auto;padding:18px;background:#fff;font-family:'Noto Sans KR',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial;color:#111827}
.page-header{display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:2px solid #e6eefc;padding-bottom:14px}
.page-kicker{margin:0 0 8px 0;font-size:1.25rem;font-weight:900;color:var(--accent-blue);text-transform:uppercase}
.title-row{display:flex;align-items:flex-start;gap:16px}
.title-accent{display:inline-block;width:8px;height:36px;background:var(--accent-blue);border-radius:3px;margin-top:4px}
.page-title{margin:0;font-size:1.6rem;font-weight:900;color:#111827}
.page-address{margin:2px 0 0 0;color:var(--accent-blue);font-size:0.95rem}
.back-link{display:inline-flex;align-items:center;gap:8px;background:none;border:none;cursor:pointer;font-weight:800;color:#111827;font-size:1.05rem;padding:6px 10px}
.hero-card{padding:18px;border-radius:12px;margin-top:16px}.hero-grid{display:grid;grid-template-columns:1fr 380px;gap:20px;align-items:start}@media(max-width:920px){.hero-grid{grid-template-columns:1fr}}
.hero-image-wrap{background:#f8fbff;border-radius:12px;overflow:hidden;aspect-ratio:4/3;display:flex;align-items:center;justify-content:center}
.hero-image{width:100%;height:100%;object-fit:cover;display:block}
.metric-lead{margin-bottom:8px}.metric-row{display:flex;align-items:center;justify-content:space-between;gap:12px}.metric-text{display:flex;flex-direction:column;gap:6px}.metric-kicker{margin:0;font-weight:800;color:var(--accent-blue)}.metric-value{margin:0;font-size:48px;font-weight:900;color:var(--color-primary-600)}.metric-sub{margin:0;color:var(--color-muted);font-size:0.95rem}
.bar-wrap{width:160px}.bar-bg{width:100%;height:18px;background:#eef6ff;border-radius:999px;position:relative;overflow:hidden}.bar-fill{height:100%;border-radius:999px;position:absolute;top:0;left:0;transition:width 500ms ease}
.metric-grid{display:flex;gap:12px;margin-top:8px}.metric-card{background:#fff;border-radius:12px;padding:10px 12px;border:1px solid #dbeafe;box-shadow:0 6px 14px rgba(31,111,235,0.04)}.metric-label{display:block;color:#6b7280;font-size:0.9rem}.metric-number{display:block;font-weight:900;font-size:1.25rem;color:#111827}
.rating-container{margin-top:16px;border-radius:12px}.rating-row{display:flex;gap:18px;align-items:center}.rating-card{flex:1;background:#fff;border-radius:18px;padding:18px;display:flex;flex-direction:column;gap:10px;align-items:center;border:1px solid #f0f5ff;box-shadow:0 8px 18px rgba(31,111,235,0.04)}.rating-kicker{align-self:flex-start;color:var(--accent-blue);font-weight:900}.rating-options{display:flex;gap:10px;justify-content:center}.rating-option{width:48px;height:48px;border-radius:999px;background:#f1f8ff;color:#1e3a8a;border:1px solid rgba(31,111,235,0.08);display:inline-flex;align-items:center;justify-content:center;font-weight:900;cursor:pointer;transition:transform .12s ease,box-shadow .12s ease}.rating-option:hover{transform:translateY(-3px)}.rating-option.active{background:var(--accent-blue);color:#fff;box-shadow:0 8px 18px rgba(31,111,235,0.12)}.rating-actions{display:flex;align-items:center;justify-content:center}.register-btn{background:var(--accent-blue);border-radius:999px;color:#fff;padding:8px 14px;font-weight:800}
.comments-section{margin-top:22px}.comments-header{display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:2px solid #e6eefc;padding-bottom:12px;margin-bottom:12px}.comments-title{margin:0;font-size:1.05rem;font-weight:900}
.comment-list{display:flex;flex-direction:column;gap:18px;padding-top:12px}.comment-item{display:flex;flex-direction:column;gap:6px}.comment-bubble{width:fit-content;max-width:84%;background:var(--bubble-bg);padding:12px 16px;border-radius:18px;position:relative;box-shadow:0 8px 16px rgba(31,111,235,0.04)}.comment-bubble::after{content:'';position:absolute;left:-10px;top:14px;width:0;height:0;border-top:8px solid transparent;border-bottom:8px solid transparent;border-right:10px solid var(--bubble-bg)}.comment-text{margin:0;color:#0f1724;line-height:1.5}.comment-meta{display:flex;align-items:center;gap:12px;color:var(--color-muted);font-size:0.9rem}.comment-delete{margin-left:auto}
.comment-compose{display:grid;grid-template-columns:150px minmax(0,1fr);gap:12px;align-items:start;padding-bottom:20px;margin-bottom:18px;border-bottom:1px solid #e6eefc}
.comment-credentials{display:flex;flex-direction:column;gap:8px}
.comment-author-input,.comment-password-input{width:100%;padding:9px 10px;border:1px solid #cbd5e1;border-radius:4px;font-size:.88rem}
.comment-author-input::placeholder,.comment-password-input::placeholder,.comment-input::placeholder{color:#b6bec9;opacity:1}
.comment-editor{display:flex;flex-direction:column;gap:8px;min-width:0}
.comment-input{width:100%;min-height:106px;border:1px solid #cbd5e1;border-radius:4px;padding:12px;background:#fff;resize:vertical}
.comment-action{display:flex;justify-content:flex-end}
.comment-submit,.native-comment{min-width:120px;background:var(--accent-blue) !important;border-radius:4px !important;color:#fff !important;padding:11px 24px !important;font-size:.95rem !important;font-weight:800 !important;border:0 !important;cursor:pointer !important;box-shadow:0 6px 14px rgba(31,111,235,0.12) !important}
.comment-submit:disabled{opacity:.6;cursor:not-allowed !important}
.native-register{background:#1f6feb !important;color:#fff !important;border-radius:999px !important;padding:12px 28px !important;font-weight:900 !important;border:0 !important;cursor:pointer !important;box-shadow:0 8px 18px rgba(31,111,235,0.2) !important}
.native-register:hover{background:#1558b0 !important}.native-register:disabled{opacity:.6;cursor:not-allowed !important}
.rating-submit-row{margin-top:12px;display:flex;justify-content:center}
.status-box{padding:20px 0;text-align:center;color:var(--color-muted)}.error-text{color:#dc2626}
@media (max-width:760px){.hero-grid{grid-template-columns:1fr}.rating-row{flex-direction:column;align-items:stretch}.register-btn{width:100%}.comment-compose{grid-template-columns:1fr}.comment-credentials{display:grid;grid-template-columns:1fr 1fr}.comment-submit{width:100%}}
</style>
