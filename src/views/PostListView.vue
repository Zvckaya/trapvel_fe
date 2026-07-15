<template>
  <div class="post-list-page">
    <section class="page-header">
      <div>
        <p class="page-kicker">Community Board</p>
        <h1 class="page-title">게시판 목록</h1>
        <p class="page-subtitle">광주/전라 여행 이야기와 후기들을 확인해보세요.</p>
      </div>

      <Button
        label="글쓰기"
        icon="pi pi-pencil"
        class="write-button"
        @click="goCreatePage"
      />
    </section>

    <Card class="search-card">
      <template #content>
        <div class="search-row">
          <span class="p-input-icon-left search-input-wrap">
            <i class="pi pi-search" />
            <InputText
              v-model="searchKeyword"
              placeholder="제목, 내용으로 검색"
              class="search-input"
            />
          </span>

          <Button
            label="검색"
            icon="pi pi-search"
            class="search-button"
            @click="applySearch"
          />
        </div>
      </template>
    </Card>

    <Card class="list-card">
      <template #content>
        <div class="post-list">
          <article
            v-for="post in posts"
            :key="post.id"
            class="post-item"
            @click="goDetailPage(post.id)"
          >
            <div class="post-item__top">
              <span class="post-item__date">{{ post.createdAt || post.created_at || '' }}</span>
            </div>

            <h2 class="post-item__title">{{ post.title }}</h2>
            <p class="post-item__summary">{{ post.summary || post.content?.slice(0, 120) || '' }}</p>

            <div class="post-item__bottom">
              <span>익명</span>
              <span>댓글 {{ post.comments ?? 0 }}</span>
            </div>
          </article>

          <div v-if="!loading && posts.length === 0" class="empty-state">
            검색 결과가 없습니다.
          </div>

          <div v-if="loading" style="padding:24px;text-align:center">로딩중...</div>
        </div>
      </template>
    </Card>

    <Paginator
      :rows="rowsPerPage"
      :totalRecords="totalRecords"
      :first="firstRecord"
      template="PrevPageLink PageLinks NextPageLink"
      class="post-paginator"
      @page="onPageChange"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Paginator from 'primevue/paginator'
import { fetchPosts } from '@/services/posts'

const router = useRouter()

const searchKeyword = ref('')
const currentPage = ref(0)
const rowsPerPage = 5

const posts = ref([])
const totalRecords = ref(0)
const loading = ref(false)

const firstRecord = computed(() => currentPage.value * rowsPerPage)

const loadPosts = async () => {
  loading.value = true
  try {
    const data = await fetchPosts({ page: currentPage.value, size: rowsPerPage, q: searchKeyword.value })
    // 응답 형식 유연 처리: { items: [], total: n } 또는 배열
    if (Array.isArray(data)) {
      posts.value = data
      totalRecords.value = data.length
    } else {
      posts.value = data.items ?? data.data ?? []
      totalRecords.value = data.total ?? posts.value.length
    }
  } catch (err) {
    console.error(err)
    posts.value = []
    totalRecords.value = 0
  } finally {
    loading.value = false
  }
}

const applySearch = () => {
  currentPage.value = 0
  loadPosts()
}

const onPageChange = (event) => {
  currentPage.value = event.page
  loadPosts()
}

watch(searchKeyword, () => {
  currentPage.value = 0
})

onMounted(() => {
  loadPosts()
})

const goDetailPage = (postId) => {
  router.push(`/posts/${postId}`)
}

const goCreatePage = () => {
  router.push('/posts/new')
}
</script>

<style scoped>
/* 기존 스타일을 그대로 재사용하셔도 됩니다 (생략 가능) */
</style>