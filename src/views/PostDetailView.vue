<template>
  <div class="post-detail-page">
    <section v-if="post" class="detail-header">
      <div>
        <p class="page-kicker">Post Detail</p>
        <h1 class="page-title">{{ post.title }}</h1>
        <p class="page-subtitle">
          {{ post.region || '' }} · {{ post.createdAt || post.created_at || '' }}
        </p>
      </div>

      <div class="action-group">
        <Button
          label="수정"
          icon="pi pi-pencil"
          class="edit-button"
          @click="goEdit"
        />
        <Button
          label="삭제"
          icon="pi pi-trash"
          severity="danger"
          outlined
          @click="openDeleteDialog"
        />
      </div>
    </section>

    <Card v-if="post" class="detail-card">
      <template #content>
        <div class="detail-meta">
          <span>작성자 {{ post.author || '익명' }}</span>
          <span>조회 {{ post.views ?? 0 }}</span>
          <span>댓글 {{ post.comments ?? 0 }}</span>
        </div>

        <div class="detail-body">
          <p v-html="post.content"></p>
        </div>
      </template>
    </Card>

    <Card v-else class="detail-card">
      <template #content>
        <p class="empty-message">게시글이 없습니다.</p>
      </template>
    </Card>

    <Dialog v-model:visible="isDeleteDialogOpen" header="삭제 확인" modal :style="{ width: '420px' }">
      <div class="password-dialog">
        <p class="password-text">게시글을 삭제하려면 비밀번호를 입력해주세요.</p>
        <InputText v-model="deletePassword" type="password" placeholder="비밀번호 입력" class="password-input" @keydown.enter="confirmDelete" />
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px">
          <Button label="취소" outlined @click="closeDeleteDialog" />
          <Button label="삭제" severity="danger" @click="confirmDelete" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import { fetchPost, deletePost } from '@/services/posts'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(false)

const isDeleteDialogOpen = ref(false)
const deletePassword = ref('')

const loadPost = async () => {
  loading.value = true
  try {
    post.value = await fetchPost(route.params.id)
  } catch (err) {
    console.error(err)
    post.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadPost)
watch(() => route.params.id, loadPost)

const goEdit = () => {
  router.push(`/posts/${route.params.id}/edit`)
}

const openDeleteDialog = () => {
  isDeleteDialogOpen.value = true
}

const closeDeleteDialog = () => {
  isDeleteDialogOpen.value = false
  deletePassword.value = ''
}

const confirmDelete = async () => {
  if (!deletePassword.value) return
  try {
    await deletePost(route.params.id, deletePassword.value)
    alert('삭제되었습니다.')
    router.push('/posts')
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || '삭제에 실패했습니다. 비밀번호를 확인하세요.')
  } finally {
    closeDeleteDialog()
  }
}
</script>

<style scoped>
/* 기존 스타일 재사용가능 */
</style>