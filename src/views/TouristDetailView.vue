<template>
  <div class="tourist-detail-page">
    <section v-if="place" class="page-header">
      <div>
        <p class="page-kicker">Tourist Review</p>
        <h1 class="page-title">{{ place.title }}</h1>
        <p class="page-subtitle">{{ place.addr1 || '주소 정보 없음' }}</p>
      </div>

      <Button label="목록으로" outlined icon="pi pi-arrow-left" @click="goBack" />
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
                <p class="metric-kicker">Water Rocket Index</p>
                <h2 class="metric-value">{{ formattedWaterRocketScore }}</h2>
                <p class="metric-copy">기대와 실제 만족도의 차이를 한눈에 보여주는 지표입니다.</p>
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

      <Card class="surface-card review-card">
        <template #content>
          <div class="section-title-row">
            <div>
              <h2 class="section-title">관광지 평가</h2>
              <p class="section-subtitle">
                방문 전 기대와 방문 후 만족도를 남기고, 아래에 댓글을 등록하세요.
              </p>
            </div>
          </div>

          <form class="review-form" @submit.prevent="submitReview">
            <div class="form-grid">
              <div class="field">
                <label for="beforeScore">방문 전 평가 평점</label>
                <select id="beforeScore" v-model.number="form.beforeScore" class="select">
                  <option v-for="score in scoreOptions" :key="`before-${score}`" :value="score">
                    {{ score }}점
                  </option>
                </select>
              </div>

              <div class="field">
                <label for="afterScore">방문 후 평가 평점</label>
                <select id="afterScore" v-model.number="form.afterScore" class="select">
                  <option v-for="score in scoreOptions" :key="`after-${score}`" :value="score">
                    {{ score }}점
                  </option>
                </select>
              </div>
            </div>

            <div class="field">
              <label for="comment">댓글</label>
              <Textarea
                id="comment"
                v-model="form.comment"
                rows="5"
                autoResize
                placeholder="관광지 경험을 자유롭게 남겨보세요."
                class="textarea"
              />
            </div>

            <div class="field">
              <label for="pw">삭제용 비밀번호 (숫자 4자리)</label>
              <input
                id="pw"
                v-model="form.password"
                inputmode="numeric"
                maxlength="4"
                placeholder="예: 1234"
                class="p-inputtext p-component"
              />
            </div>

            <div class="form-footer">
              <div class="preview-box">
                <span>입력 기준 물로켓 지수</span>
                <strong>{{ previewScore.toFixed(1) }}</strong>
              </div>

              <Button type="submit" label="평가 등록" icon="pi pi-check" :disabled="submitting" />
            </div>
          </form>
        </template>
      </Card>

      <section class="comments-section">
        <div class="section-title-row">
          <div>
            <h2 class="section-title">댓글</h2>
            <p class="section-subtitle">이 관광지에 대한 방문 경험을 확인해보세요.</p>
          </div>
          <Tag :value="`${comments.length}개`" severity="info" />
        </div>

        <Card class="surface-card comments-card">
          <template #content>
            <div v-if="loadingComments" class="status-box">댓글을 불러오는 중입니다.</div>

            <div v-else-if="comments.length > 0" class="comment-list">
              <article v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-item__top">
                  <div class="comment-head">
                    <strong class="comment-author">{{ comment.author || '익명' }}</strong>
                    <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <Button text icon="pi pi-trash" class="p-button-text" @click="confirmDelete(comment)" />
                </div>

                <p class="comment-text">{{ comment.content }}</p>
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
const scoreOptions = [1, 2, 3, 4, 5]

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

const form = reactive({
  beforeScore: 5,
  afterScore: 3,
  comment: '',
  password: '',
})

const formatValue = (value) => {
  const num = Number(value)
  if (!Number.isFinite(num)) return '-'
  return Number.isInteger(num) ? `${num}` : num.toFixed(1)
}

const formattedWaterRocketScore = computed(() => formatValue(waterRocketScore.value))
const formattedPreVisitAvg = computed(() => formatValue(preVisitAvg.value))
const formattedPostVisitAvg = computed(() => formatValue(postVisitAvg.value))
const previewScore = computed(() => form.afterScore - form.beforeScore)

const averageBy = (items, key) => {
  if (!Array.isArray(items) || items.length === 0) return null
  const values = items
    .map((item) => Number(item?.[key]))
    .filter((value) => Number.isFinite(value))
  if (values.length === 0) return null
  return values.reduce((sum, value) => sum + value, 0) / values.length
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
    const [preList, postList] = await Promise.all([
      fetchPreVisitEvaluations(backendId.value),
      fetchPostVisitEvaluations(backendId.value),
    ])

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

const submitReview = async () => {
  if (!backendId.value) return

  const text = form.comment.trim()
  if (!text) {
    alert('댓글을 입력해주세요.')
    return
  }

  if (!/^\d{4}$/.test(String(form.password))) {
    alert('비밀번호는 숫자 4자리여야 합니다.')
    return
  }

  submitting.value = true

  try {
    await createPreVisitEvaluation(backendId.value, {
      author: '익명',
      expectation_score: Number(form.beforeScore),
    })

    await createPostVisitEvaluation(backendId.value, {
      author: '익명',
      satisfaction_score: Number(form.afterScore),
    })

    await createCommentApi(backendId.value, {
      author: '익명',
      content: text,
      password: String(form.password),
    })

    form.beforeScore = 5
    form.afterScore = 3
    form.comment = ''
    form.password = ''

    await Promise.all([loadComments(), loadWaterRocketIndex(), loadEvaluationAverages()])
  } catch (error) {
    console.error('submitReview error', error)
    alert(error.response?.data?.detail || '등록에 실패했습니다.')
  } finally {
    submitting.value = false
  }
}

const confirmDelete = async (comment) => {
  const password = prompt('댓글 삭제 비밀번호 4자리를 입력해주세요.')
  if (!password) return

  if (!/^\d{4}$/.test(String(password))) {
    alert('비밀번호는 숫자 4자리여야 합니다.')
    return
  }

  try {
    await deleteCommentApi(comment.id, password)
    await Promise.all([loadComments(), loadWaterRocketIndex(), loadEvaluationAverages()])
  } catch (error) {
    console.error('deleteComment error', error)
    alert(error.response?.data?.detail || '삭제에 실패했습니다.')
  }
}

const formatDate = (iso) => {
  if (!iso) return ''
  return iso.slice(0, 10)
}

const goBack = () => {
  router.push('/tourists')
}

onMounted(() => {
  loadAll()
})

watch(
  () => route.params.id,
  () => {
    loadAll()
  },
)
</script>

<style scoped>
.tourist-detail-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header,
.section-title-row,
.hero-grid,
.form-grid,
.form-footer,
.comment-item__top,
.comment-head {
  display: flex;
}

.page-header,
.section-title-row {
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.page-kicker {
  margin: 0 0 6px;
  color: #1f6feb;
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.page-title,
.section-title {
  margin: 0;
  color: #111827;
}

.page-title {
  font-size: clamp(2rem, 3vw, 2.8rem);
  font-weight: 900;
  letter-spacing: -0.03em;
}

.page-subtitle,
.section-subtitle,
.metric-copy,
.comment-date,
.metric-label,
.metric-kicker {
  color: #6b7280;
}

.surface-card {
  border-radius: 20px;
  border: 1px solid #dbeafe;
  box-shadow: 0 8px 18px rgba(31, 111, 235, 0.06);
}

.status-box {
  padding: 18px;
  text-align: center;
  color: #6b7280;
}

.error-text {
  color: #dc2626;
}

.hero-grid {
  gap: 22px;
  align-items: stretch;
}

.hero-image-wrap {
  flex: 1.05;
  overflow: hidden;
  border-radius: 16px;
  background: #f8fbff;
}

.hero-image {
  width: 100%;
  height: 100%;
  min-height: 360px;
  object-fit: cover;
  display: block;
}

.hero-panel {
  flex: 0.95;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.metric-lead {
  padding: 22px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
}

.metric-kicker {
  margin: 0 0 8px;
  font-size: 0.9rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.metric-value {
  margin: 0;
  font-size: clamp(2.8rem, 6vw, 4.2rem);
  line-height: 1;
  color: #1f6feb;
  font-weight: 900;
}

.metric-copy {
  margin: 12px 0 0;
  line-height: 1.6;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 18px;
  border-radius: 16px;
  background: #f8fbff;
  border: 1px solid #e5eefc;
}

.metric-label {
  display: block;
  margin-bottom: 10px;
  font-size: 0.92rem;
  font-weight: 700;
}

.metric-number {
  font-size: 1.9rem;
  color: #111827;
  font-weight: 900;
}

.review-form,
.comments-section,
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-grid {
  gap: 12px;
}

.field {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
}

.select,
.textarea,
.p-inputtext {
  width: 100%;
}

.select {
  height: 42px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 0 12px;
  background: #ffffff;
}

.form-footer {
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.preview-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #374151;
}

.preview-box strong {
  font-size: 1.4rem;
  color: #1f6feb;
}

.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid #eef2ff;
}

.comment-item:last-child {
  border-bottom: 0;
}

.comment-item__top {
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.comment-head {
  flex-direction: column;
  gap: 4px;
}

.comment-author {
  color: #111827;
}

.comment-text {
  margin: 0;
  color: #374151;
  line-height: 1.6;
}

:deep(.hero-card .p-card-content),
:deep(.review-card .p-card-content),
:deep(.comments-card .p-card-content) {
  padding: 22px;
}

@media (max-width: 1024px) {
  .metric-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .page-header,
  .section-title-row,
  .hero-grid,
  .form-grid,
  .form-footer,
  .comment-item__top {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-image {
    min-height: 260px;
  }
}
</style>
