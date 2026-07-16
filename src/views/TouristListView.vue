<template>
  <div class="tourist-list-page">
    <section class="page-header">
      <div>
        <p class="page-kicker">Tourist Gallery</p>
        <h1 class="page-title">전체 관광지 목록</h1>
      </div>
    </section>

    <Card class="search-card">
      <template #content>
        <div class="search-row">
          <span class="search-input-wrap">
            <i class="pi pi-search search-input-icon" aria-hidden="true" />
            <InputText
              v-model="searchKeyword"
              placeholder="관광지명 또는 주소 검색"
              class="search-input"
              @keydown.enter="applySearch"
            />
          </span>

          <Button
            label="검색"
            icon="pi pi-search"
            class="search-button"
            :loading="loading"
            @click="applySearch"
          />
        </div>
      </template>
    </Card>

    <section class="gallery-grid">
      <article
        v-for="place in places"
        :key="place.id"
        class="place-card"
        @click="goDetailPage(place.id)"
      >
        <div class="place-image-wrap">
          <img
            :src="place.firstimage || fallbackImage"
            :alt="place.title"
            class="place-image"
          />
          <div class="place-image-badge">{{ place.region || 'Tour' }}</div>
        </div>

        <div class="place-content">
          <h2 class="place-name">{{ place.title }}</h2>
          <p class="place-address">{{ place.addr1 || '주소 정보 없음' }}</p>
        </div>
      </article>

      <div v-if="loading" class="empty-state">목록을 불러오는 중입니다.</div>
      <div v-else-if="errorMessage" class="empty-state error-state">{{ errorMessage }}</div>
      <div v-else-if="places.length === 0" class="empty-state">검색 결과가 없습니다.</div>
    </section>

    <Paginator
      :rows="rowsPerPage"
      :totalRecords="totalRecords"
      :first="firstRecord"
      template="PrevPageLink PageLinks NextPageLink"
      class="place-paginator"
      @page="onPageChange"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Paginator from 'primevue/paginator'
import { fetchLocations } from '@/services/locations'

const router = useRouter()

const fallbackImage = '/images/placeholder-place.jpg'
const rowsPerPage = 20

const places = ref([])
const totalRecords = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const searchKeyword = ref('')
const appliedKeyword = ref('')
const currentPage = ref(0)

const firstRecord = computed(() => currentPage.value * rowsPerPage)

const loadPlaces = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const data = await fetchLocations({
      page: currentPage.value + 1,
      size: rowsPerPage,
      keyword: appliedKeyword.value || undefined,
    })

    places.value = data.items ?? []
    totalRecords.value = Number(data.total ?? 0)
  } catch (error) {
    console.error('loadPlaces error', error)
    places.value = []
    totalRecords.value = 0
    errorMessage.value = '관광지 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const applySearch = async () => {
  appliedKeyword.value = searchKeyword.value.trim()
  currentPage.value = 0
  await loadPlaces()
}

const onPageChange = async (event) => {
  currentPage.value = event.page
  await loadPlaces()
}

const goDetailPage = (placeId) => {
  router.push(`/tourists/${placeId}`)
}

onMounted(() => {
  loadPlaces()
})
</script>

<style scoped>
.tourist-list-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
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

.page-title {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  color: #111827;
}

.search-card,
.place-paginator {
  border-radius: 18px;
  border: 1px solid #dbeafe;
  box-shadow: 0 8px 18px rgba(31, 111, 235, 0.06);
}

.search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.search-input-icon {
  position: absolute;
  left: 16px;
  z-index: 1;
  color: #6b7280;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
}

.search-button {
  padding: 12px 22px;
  border-radius: 999px;
  background: #1f6feb;
  border-color: #1f6feb;
}

:deep(.search-card .p-card-content) {
  padding: 18px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.place-card {
  overflow: hidden;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid #dbeafe;
  box-shadow: 0 8px 18px rgba(31, 111, 235, 0.06);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.place-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(31, 111, 235, 0.12);
}

.place-image-wrap {
  position: relative;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: #f8fbff;
}

.place-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.place-image-badge {
  position: absolute;
  left: 12px;
  top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.8);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 700;
}

.place-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
}

.place-name {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 900;
  color: #111827;
  line-height: 1.35;
}

.place-address {
  margin: 0;
  color: #6b7280;
  font-size: 0.92rem;
  line-height: 1.45;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 40px 0;
  text-align: center;
  color: #6b7280;
}

.error-state {
  color: #dc2626;
}

.place-paginator {
  padding: 6px 0;
}

:deep(.place-paginator .p-paginator-pages) {
  display: flex;
  gap: 12px;
}

:deep(.place-paginator .p-paginator-page) {
  min-width: 36px;
  height: 36px;
  border-radius: 999px;
}

@media (max-width: 1200px) {
  .gallery-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .search-row {
    flex-direction: column;
    align-items: stretch;
  }

  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .gallery-grid {
    grid-template-columns: 1fr;
  }
}
</style>
