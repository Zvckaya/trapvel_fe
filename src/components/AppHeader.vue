<template>
  <header class="app-header">
    <div class="app-header__inner">
      <RouterLink to="/" class="app-header__logo">
        <img
          src="/images/rocket-3d.png"
          alt="LocalHub"
          class="app-header__logo-image"
        />
        <span class="app-header__logo-text">Trapvel</span>
      </RouterLink>

      <nav class="app-header__nav" aria-label="주요 메뉴">
        <RouterLink to="/" class="app-header__link">홈</RouterLink>
        <RouterLink to="/tourists" class="app-header__link">관광지</RouterLink>
        <RouterLink to="/posts" class="app-header__link">게시판</RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  --color-primary: #1f6feb;
  --color-primary-hover: #1558b0;
  --color-secondary: #8ec5ff;
  --color-surface: #ffffff;
  --color-border: #dbeafe;
  --color-text-main: #111827;
  --color-text-sub: #6b7280;

  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.app-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.app-header__logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.app-header__logo-image {
  height: 52px;
  width: auto;
  display: block;
}

.app-header__logo-text {
  color: var(--color-primary);
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: -0.03em;
}

.app-header__nav {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.app-header__link {
  color: var(--color-text-sub);
  text-decoration: none;
  font-weight: 700;
  transition: color 0.2s ease;
}

.app-header__link:hover {
  color: var(--color-primary-hover);
}

.app-header__link.router-link-active {
  color: var(--color-primary);
}
</style>
