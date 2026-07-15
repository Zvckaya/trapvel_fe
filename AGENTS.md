# Repository Guidelines

## Project Structure & Module Organization
This repository is a Vue 3 + Vite frontend. Application code lives in `src/`, with route views in `src/views/`, shared UI in `src/components/`, router setup in `src/router/`, and API helpers in `src/services/`. Global styles are in `src/assets/global.css`, while static files such as logos, icons, and fonts live under `public/`. Reference documents and design assets are stored in `문서/` and should not be mixed into app code.

## Build, Test, and Development Commands
Use `npm install` to install dependencies. Start local development with `npm run dev`, build a production bundle with `npm run build`, and preview the built app with `npm run preview`. Format source files with `npm run format`; this runs Prettier against `src/`. For the chatbot endpoint smoke test, run `node test-chat.js` after confirming the target API URL is valid.

## Coding Style & Naming Conventions
Follow the existing code style: 2-space indentation, ES modules, and semicolon-free JavaScript. Keep Vue single-file components in PascalCase such as `AppHeader.vue` and view files in `*View.vue` form such as `HomeView.vue`. Use camelCase for variables and functions, and kebab-case for route names like `post-detail`. Prefer small service modules in `src/services/` for network access rather than embedding API logic across views.

## Testing Guidelines
There is no formal test runner configured yet. Until one is added, validate changes with `npm run build` and a focused manual smoke test of the affected routes. If you add tests, place them near the feature or under a dedicated `tests/` directory, and name files clearly, for example `chatbot.spec.js` or `posts.test.js`.

## Commit & Pull Request Guidelines
Recent history uses short, task-focused commit messages, often in Korean, for example `게시글 작성 페이지 수정` or `챗봇 API 연동`. Keep messages concise and specific to one change. Pull requests should include a short summary, affected screens or routes, linked issues if available, and screenshots or short recordings for UI changes.

## Configuration Tips
Environment-based endpoints are read from `VITE_API_BASE` and `VITE_CHATBOT_API_URL`. Keep secrets out of the repository, document new variables in `README.md`, and provide safe local defaults where possible.
