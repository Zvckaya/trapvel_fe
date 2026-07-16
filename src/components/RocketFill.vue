<template>
  <div
    class="rocket-wrap"
    :style="{ width: width + 'px', height: height + 'px' }"
    role="img"
    :aria-label="`물로켓 지수 ${scoreFormatted}`"
  >
    <div
      class="rocket-silhouette"
      :style="maskStyle"
    />
    <div
      class="rocket-fill"
      :style="[maskStyle, { height: fillPercent + '%', background: fillGradient }]"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: 0 },
  max: { type: Number, default: 5 },
  width: { type: [Number, String], default: 140 },
  height: { type: [Number, String], default: 120 },
  svgPath: { type: String, default: '/images/rocket-graph-0.svg' },
})

const fillPercent = computed(() => {
  const v = Number(props.score) || 0
  const abs = Math.min(Math.abs(v), props.max)
  return Math.max(0, Math.min(100, Math.round((abs / props.max) * 100)))
})

const fillGradient = computed(() =>
  Number(props.score) < 0
    ? 'linear-gradient(180deg,#ff8a8a 0%,#ff3b3b 100%)'
    : 'linear-gradient(180deg,#1f6feb 0%,#0f69ff 100%)'
)

const maskStyle = computed(() => {
  const url = `url(${props.svgPath})`
  return {
    WebkitMaskImage: url,
    WebkitMaskSize: 'contain',
    WebkitMaskPosition: 'center bottom',
    WebkitMaskRepeat: 'no-repeat',
    maskImage: url,
    maskSize: 'contain',
    maskPosition: 'center bottom',
    maskRepeat: 'no-repeat',
  }
})

const scoreFormatted = computed(() => {
  const n = Number(props.score)
  if (!Number.isFinite(n)) return '-'
  return Number.isInteger(n) ? `${n}` : n.toFixed(1)
})
</script>

<style scoped>
.rocket-wrap {
  position: relative;
  display: inline-block;
  overflow: visible;
}

.rocket-silhouette {
  position: absolute;
  inset: 0;
  background: #e6eef8;
  box-shadow: 0 6px 14px rgba(31, 111, 235, 0.04);
  pointer-events: none;
}

.rocket-fill {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0; /* anchor to bottom so height grows upward */
  height: 0%;
  transition: height 600ms cubic-bezier(.2, .9, .3, 1);
  box-shadow: 0 10px 22px rgba(31, 111, 235, 0.12);
  pointer-events: none;
}
</style>