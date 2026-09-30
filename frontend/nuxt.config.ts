// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2026-09-28',
  devtools: { enabled: false },
  typescript: {
    strict: true,
    typeCheck: true
  },
  app: {
    head: {
      title: 'CSIR Secure Web Appliance OS',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'CSIR-SWA OS Management Console' }
      ]
    }
  }
})
