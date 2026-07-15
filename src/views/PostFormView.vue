<template>
  <div class="post-form-page">
    <section class="page-header">
      <div>
        <p class="page-kicker">{{ isEditMode ? 'Edit Post' : 'Create Post' }}</p>
        <h1 class="page-title">
          {{ isEditMode ? '게시글 수정' : '게시글 작성' }}
        </h1>
        <p class="page-subtitle">
          {{ isEditMode ? '기존 게시글 내용을 수정해보세요.' : '새로운 여행 이야기를 작성해보세요.' }}
        </p>
      </div>
    </section>

    <Card class="form-card">
      <template #content>
        <form class="post-form" @submit.prevent="handleSubmit">
          <div class="form-table">
            <div class="form-row">
              <div class="form-label-cell">
                <label for="title">제목</label>
              </div>
              <div class="form-input-cell">
                <InputText id="title" v-model="form.title" placeholder="게시글 제목을 입력하세요" class="input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-label-cell">
                <label for="password">비밀번호</label>
              </div>
              <div class="form-input-cell">
                <InputText id="password" v-model="form.password" type="password" placeholder="숫자만 입력" class="input" @input="sanitizePassword" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-label-cell">
                <label for="category">지역/카테고리</label>
              </div>
              <div class="form-input-cell">
                <InputText id="category" v-model="form.category" placeholder="예: 후기, 코스, 추천 (선택)" class="input" />
              </div>
            </div>

            <div class="form-row form-row--content">
              <div class="form-label-cell">
                <label for="content">내용</label>
              </div>
              <div class="form-input-cell">
                <Textarea id="content" v-model="form.content" rows="10" autoResize placeholder="게시글 내용을 입력하세요" class="input textarea" />
              </div>
            </div>
          </div>

          <div class="button-group">
            <Button type="button" label="취소" outlined @click="goBack" />
            <Button type="submit" :label="isEditMode ? '수정 완료' : '작성 완료'" icon="pi pi-check" />
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import { createPost, fetchPost, updatePost } from '@/services/posts'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => route.path.includes('/edit'))

const form = ref({
  title: '',
  password: '',
  content: '',
  category: '',
})

const loadForEdit = async () => {
  if (!isEditMode.value) return
  try {
    const data = await fetchPost(route.params.id)
    form.value.title = data.title || ''
    form.value.content = data.content || ''
    form.value.category = data.category || ''
    // password는 빈 상태로 둡니다 (사용자가 입력해야 함)
    form.value.password = ''
  } catch (err) {
    console.error(err)
    alert('게시글을 불러오지 못했습니다.')
    router.push('/posts')
  }
}

onMounted(loadForEdit)
watch(isEditMode, loadForEdit)

const sanitizePassword = () => {
  form.value.password = (form.value.password || '').replace(/[^0-9]/g, '')
}

const handleSubmit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) {
    alert('제목과 내용을 입력하세요.')
    return
  }
  try {
    if (isEditMode.value) {
      await updatePost(route.params.id, form.value)
      router.push(`/posts/${route.params.id}`)
    } else {
      const created = await createPost(form.value)
      // backend가 id를 반환한다고 가정
      const newId = created.id ?? created.post?.id
      if (newId) router.push(`/posts/${newId}`)
      else router.push('/posts')
    }
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || '요청에 실패했습니다. 비밀번호를 확인하세요.')
  }
}

const goBack = () => {
  if (isEditMode.value) {
    router.push(`/posts/${route.params.id}`)
  } else {
    router.push('/posts')
  }
}
</script>

<style scoped>
/* 기존 스타일 재사용 */
</style>