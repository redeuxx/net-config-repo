<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats = ref(null)
const loading = ref(true)

const fetchStats = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/stats')
    stats.value = res.data
  } catch (err) {
    console.error('Error fetching stats', err)
  } finally {
    loading.value = false
  }
}

const timeAgo = (isoString) => {
  if (!isoString) return 'Never'
  const diff = Date.now() - new Date(isoString).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

const formatDate = (isoString) => {
  if (!isoString) return '—'
  return new Date(isoString).toLocaleString()
}

const coverage = computed(() => {
  if (!stats.value || !stats.value.total_devices) return 0
  const covered = stats.value.total_devices - stats.value.devices_without_configs
  return Math.round((covered / stats.value.total_devices) * 100)
})

const maxTypeCount = computed(() => {
  if (!stats.value?.device_type_breakdown?.length) return 1
  return Math.max(...stats.value.device_type_breakdown.map(t => t.count))
})

const typeColors = [
  'bg-blue-500', 'bg-indigo-500', 'bg-violet-500', 'bg-teal-500',
  'bg-cyan-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500',
]

onMounted(() => fetchStats())
</script>

<template>
  <div class="space-y-6">

    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
      <button @click="fetchStats" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex items-center space-x-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
        <span>Refresh</span>
      </button>
    </div>

    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-28 bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 animate-pulse"></div>
    </div>

    <template v-else-if="stats">

      <!-- Stat Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <!-- Total Devices -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 flex items-start space-x-4 shadow-sm">
          <div class="flex-shrink-0 w-11 h-11 rounded-lg bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm text-gray-500 dark:text-gray-400">Total Devices</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-0.5">{{ stats.total_devices }}</p>
          </div>
        </div>

        <!-- Config Coverage -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 flex items-start space-x-4 shadow-sm">
          <div class="flex-shrink-0 w-11 h-11 rounded-lg flex items-center justify-center"
            :class="coverage === 100 ? 'bg-green-100 dark:bg-green-900/40' : coverage > 50 ? 'bg-amber-100 dark:bg-amber-900/40' : 'bg-red-100 dark:bg-red-900/40'">
            <svg class="w-6 h-6" :class="coverage === 100 ? 'text-green-600 dark:text-green-400' : coverage > 50 ? 'text-amber-600 dark:text-amber-400' : 'text-red-600 dark:text-red-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm text-gray-500 dark:text-gray-400">Config Coverage</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-0.5">{{ coverage }}<span class="text-lg font-medium text-gray-400">%</span></p>
            <div class="mt-2 h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                :class="coverage === 100 ? 'bg-green-500' : coverage > 50 ? 'bg-amber-500' : 'bg-red-500'"
                :style="{ width: coverage + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Total Configs -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 flex items-start space-x-4 shadow-sm">
          <div class="flex-shrink-0 w-11 h-11 rounded-lg bg-violet-100 dark:bg-violet-900/40 flex items-center justify-center">
            <svg class="w-6 h-6 text-violet-600 dark:text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm text-gray-500 dark:text-gray-400">Configs Stored</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-0.5">{{ stats.total_configs }}</p>
          </div>
        </div>

        <!-- Configs 24h -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 flex items-start space-x-4 shadow-sm">
          <div class="flex-shrink-0 w-11 h-11 rounded-lg bg-teal-100 dark:bg-teal-900/40 flex items-center justify-center">
            <svg class="w-6 h-6 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm text-gray-500 dark:text-gray-400">Configs (24h)</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-0.5">{{ stats.configs_last_24h }}</p>
          </div>
        </div>

      </div>

      <!-- Middle Row -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">

        <!-- Device Type Breakdown -->
        <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 shadow-sm">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-4">Device Types</h3>
          <div v-if="stats.device_type_breakdown.length === 0" class="text-sm text-gray-400 dark:text-gray-500 py-4 text-center">No devices yet.</div>
          <div v-else class="space-y-3">
            <div v-for="(item, i) in stats.device_type_breakdown" :key="item.type" class="space-y-1">
              <div class="flex justify-between items-center text-sm">
                <span class="font-medium text-gray-700 dark:text-gray-300 truncate max-w-[160px]">{{ item.type }}</span>
                <span class="text-gray-500 dark:text-gray-400 ml-2 flex-shrink-0">{{ item.count }}</span>
              </div>
              <div class="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-700"
                  :class="typeColors[i % typeColors.length]"
                  :style="{ width: Math.round((item.count / maxTypeCount) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Config Activity -->
        <div class="lg:col-span-3 bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 shadow-sm">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-4">Recent Config Activity</h3>
          <div v-if="stats.recent_configs.length === 0" class="text-sm text-gray-400 dark:text-gray-500 py-4 text-center">No configs saved yet.</div>
          <ul v-else class="space-y-2">
            <li v-for="cfg in stats.recent_configs" :key="cfg.id" class="flex items-center justify-between py-2 border-b dark:border-gray-700 last:border-0">
              <div class="flex items-center space-x-3 min-w-0">
                <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ cfg.hostname || cfg.ip }}</p>
                  <p class="text-xs text-gray-400 dark:text-gray-500">{{ cfg.ip }} &middot; {{ cfg.device_type }}</p>
                </div>
              </div>
              <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 ml-3" :title="formatDate(cfg.timestamp)">{{ timeAgo(cfg.timestamp) }}</span>
            </li>
          </ul>
        </div>

      </div>

      <!-- Last Jobs Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        <!-- Last Fetch Job -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Last Config Fetch</h3>
            <span v-if="stats.last_fetch_job" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="{
                'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-400': stats.last_fetch_job.status === 'COMPLETED',
                'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-400': stats.last_fetch_job.status === 'FAILED',
                'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-400': stats.last_fetch_job.status === 'RUNNING',
              }">
              {{ stats.last_fetch_job.status }}
            </span>
          </div>
          <div v-if="!stats.last_fetch_job" class="text-sm text-gray-400 dark:text-gray-500">No fetch jobs run yet.</div>
          <div v-else class="space-y-1.5">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">Started</span>
              <span class="text-gray-700 dark:text-gray-300" :title="formatDate(stats.last_fetch_job.started_at)">{{ timeAgo(stats.last_fetch_job.started_at) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">Completed</span>
              <span class="text-gray-700 dark:text-gray-300">{{ stats.last_fetch_job.completed_at ? timeAgo(stats.last_fetch_job.completed_at) : '—' }}</span>
            </div>
            <div v-if="stats.last_fetch_job.message" class="mt-2 text-xs text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-900/50 rounded px-3 py-2 truncate">
              {{ stats.last_fetch_job.message }}
            </div>
          </div>
        </div>

        <!-- Last Scan Job -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 p-5 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Last Network Scan</h3>
            <span v-if="stats.last_scan_job" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="{
                'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-400': stats.last_scan_job.status === 'COMPLETED',
                'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-400': stats.last_scan_job.status === 'FAILED',
                'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-400': stats.last_scan_job.status === 'RUNNING',
              }">
              {{ stats.last_scan_job.status }}
            </span>
          </div>
          <div v-if="!stats.last_scan_job" class="text-sm text-gray-400 dark:text-gray-500">No scan jobs run yet.</div>
          <div v-else class="space-y-1.5">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">Range</span>
              <span class="font-mono text-gray-700 dark:text-gray-300">{{ stats.last_scan_job.cidr }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">Started</span>
              <span class="text-gray-700 dark:text-gray-300" :title="formatDate(stats.last_scan_job.started_at)">{{ timeAgo(stats.last_scan_job.started_at) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">Completed</span>
              <span class="text-gray-700 dark:text-gray-300">{{ stats.last_scan_job.completed_at ? timeAgo(stats.last_scan_job.completed_at) : '—' }}</span>
            </div>
            <div v-if="stats.last_scan_job.message" class="mt-2 text-xs text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-900/50 rounded px-3 py-2 truncate">
              {{ stats.last_scan_job.message }}
            </div>
          </div>
        </div>

      </div>

    </template>

    <div v-else class="text-sm text-gray-400 dark:text-gray-500 text-center py-12">Failed to load dashboard stats.</div>

  </div>
</template>
