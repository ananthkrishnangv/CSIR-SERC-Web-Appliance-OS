<template>
  <div class="csir-app-container">
    <!-- Top Header Bar -->
    <header class="app-header">
      <div class="header-left">
        <div class="csir-brand">
          <div class="csir-logo-placeholder">CSIR</div>
          <span class="app-title">{{ t('product_title') }}</span>
        </div>
      </div>
      <div class="header-center">
        <div class="search-box">
          <input type="text" :placeholder="t('search_placeholder')" v-model="searchQuery" />
        </div>
      </div>
      <div class="header-right">
        <!-- Language Switcher -->
        <div class="lang-selector">
          <button :class="{ active: currentLang === 'en' }" @click="setLang('en')">EN</button>
          <button :class="{ active: currentLang === 'hi' }" @click="setLang('hi')">हिन्दी</button>
          <button :class="{ active: currentLang === 'ta' }" @click="setLang('ta')">தமிழ்</button>
        </div>
        <div class="alerts-badge">
          <span class="badge-icon">🔔</span>
          <span class="alerts-label">{{ t('alerts') }}</span>
          <span class="alerts-count">5</span>
        </div>
        <div class="user-menu">
          <span class="user-name">Admin ▼</span>
        </div>
      </div>
    </header>

    <!-- Main Workspace Layout -->
    <div class="workspace-body">
      <!-- Left Navigation Sidebar -->
      <nav class="sidebar">
        <ul>
          <li :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">
            {{ t('nav.overview') }}
          </li>
          <li :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'">
            {{ t('nav.applications') }}
          </li>
          <li :class="{ active: activeTab === 'containers' }" @click="activeTab = 'applications'">
            {{ t('nav.containers') }}
          </li>
          <li :class="{ active: activeTab === 'security' }" @click="activeTab = 'security'">
            {{ t('nav.security') }}
          </li>
          <li :class="{ active: activeTab === 'ai_security' }" @click="activeTab = 'ai_security'">
            {{ t('nav.ai_security') }}
          </li>
          <li :class="{ active: activeTab === 'data_protection' }" @click="activeTab = 'data_protection'">
            {{ t('nav.data_protection') }}
          </li>
          <li :class="{ active: activeTab === 'observability' }" @click="activeTab = 'observability'">
            {{ t('nav.observability') }}
          </li>
          <li :class="{ active: activeTab === 'compliance' }" @click="activeTab = 'compliance'">
            {{ t('nav.compliance') }}
          </li>
          <li :class="{ active: activeTab === 'updates' }" @click="activeTab = 'updates'">
            {{ t('nav.updates') }}
          </li>
          <li :class="{ active: activeTab === 'boot_screen' }" @click="activeTab = 'boot_screen'">
            {{ t('nav.console_boot') }} (F2)
          </li>
        </ul>
      </nav>

      <!-- Main Dynamic Content Workspace -->
      <main class="main-content">
        <!-- Tab 1: Overview (Section 8 Mockup) -->
        <section v-if="activeTab === 'overview'" class="tab-pane">
          <h2 class="section-heading">{{ t('overview.headline') }}</h2>
          
          <!-- Headline Stat Cards -->
          <div class="headline-cards-grid">
            <div class="stat-card">
              <div class="stat-value">Health 98%</div>
              <div class="stat-sub">All nodes</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">Apps 24/24</div>
              <div class="stat-sub">Operational</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">Backups 100%</div>
              <div class="stat-sub">Last 02:00 IST</div>
            </div>
          </div>

          <!-- Split Activity & AI Recommendations -->
          <div class="split-cards-grid">
            <div class="info-card">
              <h3>{{ t('overview.security_activity_title') }}</h3>
              <div class="threat-counts">
                <span class="critical-tag">1 Critical</span>
                <span class="medium-tag">4 Medium</span>
              </div>
              <p class="activity-metric"><strong>847</strong> requests blocked by Coraza WAF</p>
              <p class="activity-metric"><strong>3</strong> IPs temporarily denied</p>
            </div>

            <div class="info-card">
              <h3>{{ t('overview.ai_recommendations_title') }}</h3>
              <ul class="ai-rec-list">
                <li v-for="rec in aiRecs" :key="rec.rec_id">
                  • {{ rec.title }}
                  <span :class="['pill-badge', rec.impact]">{{ rec.impact }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Application Health Table -->
          <div class="table-container">
            <h3>{{ t('overview.application_health_title') }}</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>WAF</th>
                  <th>Backup</th>
                  <th>CPU</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.app_id">
                  <td><strong>{{ app.name }}</strong></td>
                  <td>
                    <span :class="['status-indicator', app.health]">
                      {{ app.health === 'healthy' ? 'Healthy' : 'Warning' }}
                    </span>
                  </td>
                  <td>{{ app.waf }}</td>
                  <td>{{ app.backup }}</td>
                  <td>{{ app.cpu }}</td>
                  <td>
                    <button class="btn-sm" @click="triggerAppAction(app.app_id, 'restart')">Restart</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Quick Actions matching Section 8 -->
          <div class="action-bar">
            <button class="btn-action" @click="activeTab = 'security'">[{{ t('overview.actions.view_incidents') }}]</button>
            <button class="btn-action primary" @click="openDeployModal">[{{ t('overview.actions.deploy_app') }}]</button>
            <button class="btn-action" @click="runResticBackup">[{{ t('overview.actions.run_backup') }}]</button>
            <button class="btn-action" @click="verifyAuditChain">[{{ t('overview.actions.verify_audit') }}]</button>
          </div>
        </section>

        <!-- Tab: Boot Screen Emulator (Section 6 Mockup) -->
        <section v-if="activeTab === 'boot_screen'" class="tab-pane">
          <div class="terminal-container">
            <pre class="ascii-boot-screen">{{ bootScreenText }}</pre>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const activeTab = ref('overview')
const currentLang = ref('en')
const searchQuery = ref('')

const applications = ref<any[]>([])
const aiRecs = ref<any[]>([])

const bootScreenText = `
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                         [ APPROVED CSIR LOGO ]                       │
│                                                                      │
│                    CSIR SECURE WEB APPLIANCE OS                      │
│             Immutable Web, Application and Security Platform         │
│                                                                      │
│                     Version 1.0.0 | Stable Channel                   │
│                                                                      │
│     Initialising immutable operating system ................. OK     │
│     Verifying signed platform image ......................... OK     │
│     Validating TPM and Secure Boot .......................... OK     │
│     Mounting encrypted appliance data ....................... OK     │
│     Starting management services ............................ OK     │
│     Starting web protection services ....................... OK     │
│     Checking backup repository .............................. OK     │
│                                                                      │
│              Management: https://10.20.10.15:8443                    │
│              Console: Press F2    Recovery: Press F8                 │
│                                                                      │
│ This system is restricted to authorised users. Activity may be       │
│ monitored, recorded and retained for security and compliance.        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
`

function setLang(lang: string) {
  currentLang.value = lang
}

function t(key: string): string {
  // Simple key resolver for template
  return key
}

function openDeployModal() {
  alert('Deploy new Quadlet workload wizard.')
}

async function triggerAppAction(appId: string, action: string) {
  // Dispatches to /api/v1/applications/{app_id}/action
}

async function runResticBackup() {
  // Dispatches to /api/v1/backups/runs/trigger
}

async function verifyAuditChain() {
  // Dispatches to /api/v1/audit/verify
}
</script>

<style scoped>
.csir-app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f8fafc;
  color: #0f172a;
}
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background-color: #ffffff;
  border-bottom: 2px solid #e2e8f0;
}
.csir-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.csir-logo-placeholder {
  background: #1e3a8a;
  color: #fff;
  padding: 4px 8px;
  font-weight: bold;
  border-radius: 4px;
}
.app-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #1e293b;
}
.workspace-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.sidebar {
  width: 240px;
  background: #ffffff;
  border-right: 1px solid #cbd5e1;
}
.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar li {
  padding: 12px 20px;
  cursor: pointer;
  border-left: 4px solid transparent;
  font-size: 0.95rem;
  color: #334155;
}
.sidebar li:hover {
  background: #f1f5f9;
}
.sidebar li.active {
  background: #e0f2fe;
  color: #0284c7;
  border-left-color: #0284c7;
  font-weight: 600;
}
.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
.headline-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 16px;
  text-align: center;
}
.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
}
.split-cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}
.info-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 16px;
}
.table-container {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th, .data-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}
.action-bar {
  display: flex;
  gap: 12px;
}
.btn-action {
  padding: 8px 16px;
  background: #f8fafc;
  border: 1px solid #94a3b8;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}
.btn-action.primary {
  background: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
}
.ascii-boot-screen {
  background: #090d16;
  color: #38bdf8;
  padding: 24px;
  border-radius: 8px;
  font-family: monospace;
  line-height: 1.3;
}
</style>
