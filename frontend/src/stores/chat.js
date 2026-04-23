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
        loadingStage: '',          // current stage message shown in LoadingExperience
        itinerary: null,           // active single itinerary
        variations: null,          // array of 3 itinerary variations (Feature 1)
        activeVariationIndex: 0,   // which tab is selected (0=Classic, 1=Hidden, 2=Balanced)
        mixedDays: [],             // Pick & Mix custom days
        currentPreferences: null,
    }),

    getters: {
        activeVariation(state) {
            if (!state.variations || !state.variations.length) return null
            return state.variations[state.activeVariationIndex] || state.variations[0]
        },
        displayItinerary(state) {
            // Show active variation if we have multi, otherwise single
            if (state.variations && state.variations.length) {
                return state.variations[state.activeVariationIndex] || null
            }
            return state.itinerary
        },
    },

    actions: {
        setVariation(index) {
            this.activeVariationIndex = index
            // Sync single itinerary to the selected variation so components work without change
            if (this.variations && this.variations[index]) {
                this.itinerary = this.variations[index]
            }
        },

        async generateItinerary(formData) {
            this.isLoading = true
            this.variations = null
            this.itinerary = null
            const authStore = useAuthStore()

            const stages = [
                'Analysing your preferences...',
                'Exploring 500+ attractions...',
                'Optimising for weather...',
                'Crafting your perfect itinerary...',
                'Adding final touches...',
            ]
            let stageIdx = 0
            this.loadingStage = stages[0]
            const stageTimer = setInterval(() => {
                stageIdx = Math.min(stageIdx + 1, stages.length - 1)
                this.loadingStage = stages[stageIdx]
            }, 5000)

            try {
                if (typeof formData === 'object') this.currentPreferences = formData

                const response = await axios.post(
                    '/api/v1/plan/',
                    { preferences: formData },
                    { headers: { Authorization: `Bearer ${authStore.token}` } }
                )

                if (response.data && response.data.days) {
                    this.itinerary = response.data
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: `✅ I've created "${response.data.title}" for you! Check the dashboard.`,
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
                clearInterval(stageTimer)
                this.isLoading = false
                this.loadingStage = ''
            }
        },

        async generateMultiItinerary(formData) {
            this.isLoading = true
            this.variations = null
            this.itinerary = null
            this.activeVariationIndex = 0
            const authStore = useAuthStore()

            const stages = [
                'Generating The Classic route...',
                'Discovering Hidden Gems...',
                'Crafting the Balanced Mix...',
                'Optimising all 3 variations for weather...',
                'Finalising your personalised options...',
            ]
            let stageIdx = 0
            this.loadingStage = stages[0]
            const stageTimer = setInterval(() => {
                stageIdx = Math.min(stageIdx + 1, stages.length - 1)
                this.loadingStage = stages[stageIdx]
            }, 8000)

            try {
                if (typeof formData === 'object') this.currentPreferences = formData

                const response = await axios.post(
                    '/api/v1/plan/multi/',
                    { preferences: formData },
                    { headers: { Authorization: `Bearer ${authStore.token}` } }
                )

                if (response.data && response.data.variations) {
                    this.variations = response.data.variations.filter(v => !v.error)
                    if (this.variations.length) {
                        this.itinerary = this.variations[0]
                        this.messages.push({
                            id: Date.now() + 1,
                            role: 'assistant',
                            content: `✅ I've generated ${this.variations.length} itinerary variations! Pick your favourite or mix and match days.`,
                        })
                    }
                } else {
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: "Couldn't generate variations. Please try again.",
                    })
                }
            } catch (error) {
                console.error('Multi-plan Error:', error)
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: 'Sorry, multi-variation generation failed. Please try again.',
                })
            } finally {
                clearInterval(stageTimer)
                this.isLoading = false
                this.loadingStage = ''
            }
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
