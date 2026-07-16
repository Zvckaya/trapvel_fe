<template>
  <div class="home-page">
    <section class="landing-section">
      <p class="landing-kicker">기대와 실제 만족도의 차이로 보는 관광지 랭킹</p>

      <h1 class="landing-title">
        기대보다 <span>더 좋았던 곳</span>과 아쉬웠던 곳
      </h1>

      <p class="landing-subtitle">실제 방문 평가와 최근 댓글을 함께 확인하세요.</p>

      <div class="brand-block">
        <p class="brand-en">Trapvel,</p>
        <p class="brand-ko">트랩블</p>
      </div>

      <div class="landing-visual">
        <img
          src="/images/rocket-3d.png"
          alt="물로켓 3D 아이콘"
          class="rocket-image"
        />
      </div>

      <p class="landing-message">
        기대와 다른 여행, 혹시 <strong>트랩(Trap)</strong>은 아니었나요?
      </p>

      <button class="cta-button" @click="scrollToMainContent">
        물로켓 지수 확인하기
      </button>
    </section>

    <section ref="mainContentRef" class="main-content-section">
      <div class="section-header">
        <h2 class="section-title">물로켓 지수 하위 3곳</h2>
        <p class="section-subtitle">
          기대와 실제 만족도의 차이가 작았던 관광지입니다.
        </p>
      </div>

      <div class="card-grid">
        <Card
          v-for="item in rocketTop3"
          :key="item.id"
          class="rank-card"
          @click="goTouristDetail(item.id)"
        >
          <template #header>
            <img
              :src="item.mainImage || item.thumbnailImage || fallbackImage"
              :alt="item.name"
              class="rank-card-image"
            />
          </template>

          <template #title>
            <div class="card-title-row">
              <span class="card-title-text">{{ item.name }}</span>
              <span class="rank-badge">{{ item.rank }}위</span>
            </div>
          </template>

          <template #content>
            <div class="card-body">
              <p class="card-description">
                {{ item.address || '주소 정보 없음' }}
              </p>
              <div class="card-meta">
                <span class="score-badge score-badge--low">
                  물로켓 지수 {{ formatScore(item.score) }}
                </span>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <div v-if="isLoadingExtremes" class="section-empty">물로켓 지수를 불러오는 중입니다.</div>
      <div v-else-if="extremesError" class="section-error">{{ extremesError }}</div>
      <div v-else-if="rocketTop3.length === 0" class="section-empty">표시할 데이터가 없습니다.</div>

      <div class="section-header">
        <h2 class="section-title">물로켓 지수 상위 3곳</h2>
        <p class="section-subtitle">
          기대보다 실제 만족도가 낮아 아쉬움이 컸던 관광지입니다.
        </p>
      </div>

      <div class="card-grid">
        <Card
          v-for="item in rocketBottom3"
          :key="item.id"
          class="rank-card"
          @click="goTouristDetail(item.id)"
        >
          <template #header>
            <img
              :src="item.mainImage || item.thumbnailImage || fallbackImage"
              :alt="item.name"
              class="rank-card-image"
            />
          </template>

          <template #title>
            <div class="card-title-row">
              <span class="card-title-text">{{ item.name }}</span>
              <span class="rank-badge place">{{ item.rank }}위</span>
            </div>
          </template>

          <template #content>
            <div class="card-body">
              <p class="card-description">
                {{ item.address || '주소 정보 없음' }}
              </p>
              <div class="card-meta">
                <span class="score-badge score-badge--high">
                  물로켓 지수 {{ formatScore(item.score) }}
                </span>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <div
        v-if="!isLoadingExtremes && !extremesError && rocketBottom3.length === 0"
        class="section-empty"
      >
        표시할 데이터가 없습니다.
      </div>

      <div class="section-header">
        <h2 class="section-title">최근 댓글</h2>
        <p class="section-subtitle">
          방금 등록된 관광지 댓글을 확인해보세요.
        </p>
      </div>

      <Card class="post-card">
        <template #content>
          <div class="post-list">
            <article
              v-for="comment in recentComments"
              :key="comment.id"
              class="post-item"
              role="link"
              tabindex="0"
              @click="goTouristDetail(comment.locationId)"
              @keydown.enter="goTouristDetail(comment.locationId)"
            >
              <div class="post-item__top">
                <h3 class="post-item__title">{{ comment.locationTitle }}</h3>
                <span class="post-item__author">{{ comment.author }}</span>
              </div>
              <p class="post-item__summary">{{ comment.summary }}</p>
            </article>
          </div>
          <div v-if="isLoadingComments" class="section-empty">최근 댓글을 불러오는 중입니다.</div>
          <div v-else-if="recentComments.length === 0" class="section-empty">최근 댓글이 없습니다.</div>
        </template>
      </Card>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import { fetchWaterRocketExtremes } from '@/services/locations'
import { fetchRecentComments } from '@/services/comment'

const router = useRouter()
const fallbackImage = '/images/placeholder-place.jpg'

const mainContentRef = ref(null)
const isLoadingExtremes = ref(false)
const extremesError = ref('')
const rocketTop3 = ref([])
const rocketBottom3 = ref([])
const isLoadingComments = ref(false)
const recentComments = ref([])

const scrollToMainContent = () => {
  if (!mainContentRef.value) return
  mainContentRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const mapLocationCard = (item, index) => ({
  id: item.id,
  rank: index + 1,
  name: item.title || `관광지 #${item.id}`,
  address: item.addr1 || '',
  mainImage: item.firstimage || item.firstimage2 || '',
  thumbnailImage: item.firstimage2 || item.firstimage || '',
  score: Number(item.water_rocket_index ?? 0),
})

const formatScore = (score) => {
  const value = Number(score ?? 0)
  return Number.isInteger(value) ? `${value}` : value.toFixed(1)
}

const loadWaterRocketExtremes = async () => {
  isLoadingExtremes.value = true
  extremesError.value = ''

  try {
    const data = await fetchWaterRocketExtremes(3)
    rocketTop3.value = (data.highest ?? []).map(mapLocationCard)
    rocketBottom3.value = (data.lowest ?? []).map(mapLocationCard)
  } catch (error) {
    console.error('failed to load water rocket extremes', error)
    extremesError.value = '물로켓 지수 데이터를 불러오지 못했습니다.'
  } finally {
    isLoadingExtremes.value = false
  }
}

const loadRecentComments = async () => {
  isLoadingComments.value = true

  try {
    const data = await fetchRecentComments(3)
    recentComments.value = (data ?? []).map((item) => ({
      id: item.id,
      locationId: item.location_id,
      locationContentId: item.location_content_id,
      locationTitle: item.location_title || '관광지 정보 없음',
      author: item.author || '익명',
      summary: item.content || '',
    }))
  } catch (error) {
    console.error('failed to load recent comments', error)
    recentComments.value = []
  } finally {
    isLoadingComments.value = false
  }
}

const goTouristDetail = (placeId) => {
  router.push(`/tourists/${placeId}`)
}

onMounted(() => {
  loadWaterRocketExtremes()
  loadRecentComments()
})
</script>

<style scoped>
.home-page {
  color: #111827;
}

.landing-section {
  min-height: calc(100vh - 88px);
  max-width: 980px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 72px 20px 90px;
  text-align: center;
}

.landing-kicker {
  margin: 0 0 8px;
  font-size: 1.1rem;
  line-height: 1.55;
  color: #6b7280;
  letter-spacing: -0.01em;
}

.landing-title {
  margin: 0;
  font-size: clamp(2.5rem, 5vw, 4.6rem);
  line-height: 1.18;
  font-weight: 800;
  letter-spacing: -0.035em;
  color: #111827;
}

.landing-title span {
  color: #1f6feb;
}

.landing-subtitle {
  margin: 2px 0 0;
  font-size: clamp(1.25rem, 2.2vw, 1.9rem);
  line-height: 1.45;
  color: #374151;
  letter-spacing: -0.02em;
}

.brand-block {
  margin-top: 18px;
}

.brand-en {
  margin: 0;
  font-size: clamp(3rem, 5.5vw, 5rem);
  line-height: 1.02;
  font-weight: 900;
  color: #1f6feb;
  letter-spacing: -0.03em;
}

.brand-ko {
  margin: 2px 0 0;
  font-size: clamp(2.6rem, 4.6vw, 4rem);
  line-height: 1.04;
  font-weight: 900;
  color: #111827;
  letter-spacing: -0.03em;
}

.landing-visual {
  margin: 18px 0 10px;
  display: flex;
  justify-content: center;
  width: 100%;
}

.rocket-image {
  width: min(620px, 72vw);
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 18px 28px rgba(31, 111, 235, 0.2));
  transform: rotate(-8deg);
}

.landing-message {
  margin: 8px 0 0;
  font-size: clamp(1.3rem, 2.3vw, 2rem);
  line-height: 1.45;
  letter-spacing: -0.02em;
  color: #111827;
}

.landing-message strong {
  color: #1f6feb;
}

.cta-button {
  margin-top: 18px;
  width: fit-content;
  align-self: center;
  border: 0;
  border-radius: 999px;
  background: #1f6feb;
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  padding: 15px 34px;
  box-shadow: 0 10px 24px rgba(31, 111, 235, 0.24);
  cursor: pointer;
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.cta-button:hover {
  background: #1558b0;
  transform: translateY(-2px);
}

.main-content-section {
  padding: 48px 0 72px;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  margin: 0 0 6px;
  font-size: 1.6rem;
  font-weight: 800;
  color: #111827;
}

.section-subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.98rem;
  line-height: 1.5;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.rank-card {
  border-radius: 18px;
  border: 1px solid #dbeafe;
  overflow: hidden;
  box-shadow: 0 8px 18px rgba(31, 111, 235, 0.06);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.rank-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(31, 111, 235, 0.12);
}

.rank-card-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1f6feb;
  font-size: 0.85rem;
  font-weight: 800;
}

.rank-badge.place {
  background: #e0f2fe;
  color: #0284c7;
}

.card-title-text {
  flex: 1;
  min-width: 0;
  font-size: 1.25rem;
  line-height: 1.35;
  font-weight: 900;
  letter-spacing: -0.025em;
  color: #111827;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-description {
  margin: 0;
  color: #9ca3af;
  font-size: 0.85rem;
  line-height: 1.45;
  word-break: keep-all;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.score-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 800;
}

.score-badge--high {
  background: #fee2e2;
  color: #dc2626;
}

.score-badge--low {
  background: #e0f2fe;
  color: #0284c7;
}

.section-empty,
.section-error {
  margin: -8px 0 28px;
  color: #6b7280;
  font-size: 0.95rem;
}

.section-error {
  color: #dc2626;
}

.post-card {
  border-radius: 18px;
  border: 1px solid #dbeafe;
  box-shadow: 0 8px 18px rgba(31, 111, 235, 0.06);
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.post-item {
  padding: 14px 0;
  border-bottom: 1px solid #eef2ff;
  cursor: pointer;
}

.post-item:last-child {
  border-bottom: 0;
}

.post-item__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.post-item__title {
  margin: 0;
  font-size: 1.18rem;
  font-weight: 800;
  color: #111827;
}

.post-item__author {
  flex-shrink: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.post-item__summary {
  margin: 0;
  color: #4b5563;
  line-height: 1.55;
  word-break: keep-all;
}

.post-item:focus {
  outline: 3px solid rgba(31, 111, 235, 0.12);
  outline-offset: 4px;
  border-radius: 8px;
}

:deep(.rank-card .p-card-body) {
  padding: 0;
}

:deep(.rank-card .p-card-title) {
  padding: 16px 18px 0;
  margin: 0;
}

:deep(.rank-card .p-card-content) {
  padding: 14px 18px 18px;
}

:deep(.post-card .p-card-content) {
  padding: 18px;
}

@media (max-width: 1024px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
