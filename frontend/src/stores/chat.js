import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', {
    state: () => ({
        messages: [
            {
                id: 1,
                role: 'assistant',
                content: 'Hi! I am your Sri Lanka Travel Agent. Tell me about your dream trip, or use the form to generate your itinerary.'
            }
        ],
        isLoading: false,
        loadingStage: '',
        progress: 0,           // 0-100 for the progress bar
        itinerary: null,
        variations: null,
        activeVariationIndex: 0,
        mixedDays: [],
        currentPreferences: null,
    }),

    getters: {
        activeVariation(state) {
            if (!state.variations || !state.variations.length) return null
            return state.variations[state.activeVariationIndex] || state.variations[0]
        },
        displayItinerary(state) {
            if (state.variations && state.variations.length) {
                return state.variations[state.activeVariationIndex] || null
            }
            return state.itinerary
        },
    },

    actions: {
        setVariation(index) {
            this.activeVariationIndex = index
            if (this.variations && this.variations[index]) {
                this.itinerary = this.variations[index]
            }
        },

        // --- Single itinerary (async Celery path) ---
        async generateItinerary(formData) {
            this.isLoading = true
            this.variations = null
            this.itinerary = null
            this.progress = 0
            this.loadingStage = 'Submitting your request...'
            const authStore = useAuthStore()

            try {
                if (typeof formData === 'object') this.currentPreferences = formData

                // Submit job
                const submit = await axios.post(
                    '/api/v1/plan/async/',
                    { preferences: formData },
                    { headers: { Authorization: `Bearer ${authStore.token}` } }
                )
                const jobId = submit.data.job_id
                this.loadingStage = 'Generating your perfect itinerary...'
                this.progress = 10

                // Poll for result
                const result = await this._pollJob(jobId, authStore.token)

                if (result && result.days) {
                    this.itinerary = result
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: `✅ I've created "${result.title}" for you! Check the dashboard.`,
                    })
                } else {
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: "I couldn't generate a plan. Please try again.",
                    })
                }
            } catch (error) {
                console.error('Plan Error:', error)
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: 'Sorry, I had trouble creating the plan. Please try again.',
                })
            } finally {
                this.isLoading = false
                this.loadingStage = ''
                this.progress = 0
            }
        },

        // --- Multi-variation itinerary (async Celery path) ---
        async generateMultiItinerary(formData) {
            this.isLoading = true
            this.variations = null
            this.itinerary = null
            this.activeVariationIndex = 0
            this.progress = 0
            this.loadingStage = 'Submitting your request...'
            const authStore = useAuthStore()

            try {
                if (typeof formData === 'object') this.currentPreferences = formData

                // Submit job
                const submit = await axios.post(
                    '/api/v1/plan/multi/async/',
                    { preferences: formData },
                    { headers: { Authorization: `Bearer ${authStore.token}` } }
                )
                const jobId = submit.data.job_id
                this.loadingStage = 'Generating 3 variations...'
                this.progress = 5

                // Poll for result
                const result = await this._pollJob(jobId, authStore.token)

                if (result && result.variations) {
                    const valid = result.variations.filter(v => v && !v.error && v.days)
                    if (valid.length) {
                        this.variations = valid
                        this.itinerary = valid[0]
                        this.messages.push({
                            id: Date.now() + 1,
                            role: 'assistant',
                            content: `✅ I've generated ${valid.length} itinerary variation${valid.length > 1 ? 's' : ''}! Pick your favourite or mix and match days.`,
                        })
                    } else {
                        this.variations = null
                        this.messages.push({
                            id: Date.now() + 1,
                            role: 'assistant',
                            content: '⚠️ The AI model returned no valid itineraries. Please try again.',
                        })
                    }
                } else {
                    this.variations = null
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: "Couldn't generate variations. Please try again.",
                    })
                }
            } catch (error) {
                console.error('Multi-plan Error:', error)
                this.variations = null
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: 'Sorry, multi-variation generation failed. Please try again.',
                })
            } finally {
                this.isLoading = false
                this.loadingStage = ''
                this.progress = 0
            }
        },

        // --- Internal: poll /api/v1/plan/status/<jobId>/ until done ---
        _pollJob(jobId, token) {
            return new Promise((resolve, reject) => {
                const interval = setInterval(async () => {
                    try {
                        const res = await axios.get(
                            `/api/v1/plan/status/${jobId}/`,
                            { headers: { Authorization: `Bearer ${token}` } }
                        )
                        const { status, progress, message, result } = res.data

                        if (progress !== undefined) this.progress = progress
                        if (message) this.loadingStage = message

                        if (status === 'done') {
                            clearInterval(interval)
                            resolve(result)
                        } else if (status === 'error') {
                            clearInterval(interval)
                            reject(new Error(message || 'Generation failed'))
                        }
                        // 'pending' / 'processing' — keep polling
                    } catch (err) {
                        clearInterval(interval)
                        reject(err)
                    }
                }, 2000)
            })
        },

        loadSavedItinerary(tripJson) {
            this.itinerary = tripJson
            this.variations = null
            this.messages.push({
                id: Date.now(),
                role: 'assistant',
                content: `I've opened your saved trip: ${tripJson.title}! Hit "Start Journey" when ready.`,
            })
        },

        async sendMessage(text) {
            this.messages.push({ id: Date.now(), role: 'user', content: text })
            this.isLoading = true
            const authStore = useAuthStore()

            try {
                const response = await axios.post(
                    '/api/v1/plan/',
                    { preferences: text },
                    { headers: { Authorization: `Bearer ${authStore.token}` } }
                )

                if (response.data && response.data.days) {
                    this.itinerary = response.data
                    this.variations = null
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: `✅ Created "${response.data.title}"! Check the dashboard.`,
                    })
                } else if (response.data && response.data.chat_response) {
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: response.data.chat_response,
                    })
                } else {
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: "I couldn't generate a response. Please try being more specific.",
                    })
                }
            } catch (error) {
                console.error('Chat Error:', error)
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: 'Sorry, I encountered an error connecting to the AI.',
                })
            } finally {
                this.isLoading = false
            }
        },
    },
})
