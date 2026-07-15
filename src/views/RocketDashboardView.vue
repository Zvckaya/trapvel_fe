<template>
  <div class="rocket-dashboard-page">
    <RouterLink to="/tourists" class="page-header-link">
      <section class="page-header">
        <div>
          <p class="page-kicker">Rocket Index</p>
          <h1 class="page-title">물로켓 지수 대시보드</h1>
          <p class="page-subtitle">
            기대와 실제 만족도의 차이를 바탕으로 관광지별 과대평가 지수를 보여줘요.
          </p>
        </div>
      </section>
    </RouterLink>

    <section class="summary-grid">
      <Card class="summary-card">
        <template #content>
          <p class="summary-label">전체 관광지 수</p>
          <h2 class="summary-value">{{ summary.totalPlaces }}</h2>
        </template>
      </Card>

      <Card class="summary-card">
        <template #content>
          <p class="summary-label">평균 물로켓 지수</p>
          <h2 class="summary-value">{{ summary.averageScore }}점</h2>
        </template>
      </Card>

      <Card class="summary-card">
        <template #content>
          <p class="summary-label">평가가 등록된 관광지</p>
          <h2 class="summary-value">{{ summary.validPlaces }}</h2>
        </template>
      </Card>
    </section>

    <section class="content-grid">
      <Card class="ranking-card">
        <template #title>
          <div class="section-title-row">
            <span>관광지 랭킹</span>
            <Tag value="TOP 5" severity="danger" />
          </div>
        </template>

        <template #content>
          <div class="ranking-list">
            <article
              v-for="place in rocketRanking"
              :key="place.id"
              class="ranking-item"
              @click="goTouristDetail(place.id)"
            >
              <div class="ranking-item__left">
                <span class="rank-badge">{{ place.rank }}위</span>
                <div>
                  <h3 class="place-name">{{ place.name }}</h3>
                  <p class="place-meta">
                    관광 전 {{ place.expectation }}점 · 관광 후 {{ place.satisfaction }}점
                  </p>
                </div>
              </div>

              <div class="ranking-item__right">
                <Tag :value="`${place.score}점`" :severity="getSeverity(place.score)" />
                <span class="review-count">후기 {{ place.reviewCount }}개</span>
              </div>
            </article>
          </div>
        </template>
      </Card>

      <Card class="chart-card">
        <template #title>
          <div class="section-title-row">
            <span>물로켓 지수 차트</span>
            <Tag value="BAR CHART" severity="info" />
          </div>
        </template>

        <template #content>
          <div class="chart-wrap">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </template>
      </Card>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bar } from 'vue-chartjs'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import { getTouristPlaceById, touristPlaces } from '@/assets/data/touristPlaces'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const router = useRouter()

const reviewStats = [
  { id: '126385', expectation: 4.6, satisfaction: 2.2, reviewCount: 18 },
  { id: '127065', expectation: 4.3, satisfaction: 2.5, reviewCount: 15 },
  { id: '742332', expectation: 4.1, satisfaction: 2.7, reviewCount: 12 },
  { id: '1622203', expectation: 4.7, satisfaction: 3.2, reviewCount: 11 },
  { id: '2565865', expectation: 4.5, satisfaction: 3.4, reviewCount: 10 },
]

const enrichedRanking = reviewStats
  .map((item) => {
    const place = getTouristPlaceById(item.id)

    if (!place) return null

    return {
      ...place,
      ...item,
      score: Number((item.expectation - item.satisfaction).toFixed(1)),
    }
  })
  .filter(Boolean)
  .sort((left, right) => right.score - left.score)

const rocketRanking = enrichedRanking.map((item, index) => ({
  ...item,
  rank: index + 1,
}))

const summary = computed(() => {
  const totalPlaces = touristPlaces.length

  const averageScore =
    rocketRanking.length > 0
      ? (
          rocketRanking.reduce((sum, item) => sum + item.score, 0) / rocketRanking.length
        ).toFixed(1)
      : '0.0'

  const validPlaces = rocketRanking.length

  return {
    totalPlaces,
    averageScore,
    validPlaces,
  }
})

const chartData = computed(() => ({
  labels: rocketRanking.map((place) => place.name),
  datasets: [
    {
      label: '물로켓 지수',
      data: rocketRanking.map((place) => place.score),
      backgroundColor: ['#DC3545', '#DC3545', '#FFC107', '#FFC107', '#40C057'],
      borderRadius: 10,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context) => `${context.raw}점`,
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 5,
      ticks: {
        stepSize: 1,
      },
      grid: {
        color: '#e5eefc',
      },
    },
    x: {
      grid: {
        display: false,
      },
    },
  },
}

const getSeverity = (score) => {
  if (score >= 2.0) return 'danger'
  if (score >= 1.0) return 'warning'
  return 'success'
}

const goTouristDetail = (placeId) => {
  router.push(`/tourists/${placeId}`)
}
</script>

<style scoped>
.rocket-dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-header-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.page-kicker {
  margin: 0 0 6px;
  color: #1f6feb;
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.page-title {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  color: #111827;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #6b7280;
  line-height: 1.5;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.summary-card,
.ranking-card,
.chart-card {
  border-radius: 18px;
  border: 1px solid #dbeafe;
  box-shadow: 0 8px 18px rgba(31, 111, 235, 0.06);
}

.summary-label {
  margin: 0 0 8px;
  color: #6b7280;
  font-size: 0.95rem;
}

.summary-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 900;
  color: #1f6feb;
  letter-spacing: -0.03em;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 14px;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 800;
  color: #111827;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #eef2ff;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.ranking-item:hover {
  transform: translateY(-1px);
}

.ranking-item:last-child {
  border-bottom: 0;
}

.ranking-item__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1f6feb;
  font-size: 0.85rem;
  font-weight: 800;
}

.place-name {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 800;
  color: #111827;
}

.place-meta {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 0.92rem;
}

.ranking-item__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.review-count {
  color: #6b7280;
  font-size: 0.9rem;
}

.chart-wrap {
  height: 360px;
}

@media (max-width: 1024px) {
  .summary-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>