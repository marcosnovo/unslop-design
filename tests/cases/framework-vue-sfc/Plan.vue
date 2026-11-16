<template>
  <section class="plan">
    <h2 class="plan-title">Team plan</h2>
    <p>{{ seats }} seat(s) left</p>
  </section>
</template>

<style scoped>
.plan { border-left: 4px solid var(--brand); border-radius: 16px; padding: 24px; }
.plan-title { font-family: "Fira Code", monospace; }
</style>
