import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', {
    state: () => ({
        messages: [
            {
                id: 1,
                role: 'assistant',
                content: 'Hi! I am your Sri Lanka Travel Agent. Tell me about your dream trip (e.g., "7 days beach and culture").'
            }
        ],
        isLoading: false,
        itinerary: null, // Store the generated JSON itinerary here
        currentPreferences: null // Store the structured formData used to generate it
    }),

    actions: {
        async generateItinerary(formData) {
            this.isLoading = true
            const authStore = useAuthStore()

            try {
                // Save preferences for editing later
                if (typeof formData === 'object') {
                    this.currentPreferences = formData;
                }

                // Send the structured object directly
                const response = await axios.post('/api/v1/plan/',
                    { preferences: formData }, // Backend now expects this to be dict OR string
                    {
                        headers: {
                            'Authorization': `Bearer ${authStore.token}`
                        }
                    }
                )

                // Handle Response
                if (response.data && response.data.days) {
                    this.itinerary = response.data
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: `I've created a ${response.data.title} for you! Check the dashboard on the right.`
                    })
                } else {
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: "I couldn't generate a plan. Please try again."
                    })
                }
            } catch (error) {
                console.error("Plan Error:", error)
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: "Sorry, I had trouble creating the plan. Please try again."
                })
            } finally {
                this.isLoading = false
            }
        },

        loadSavedItinerary(tripJson) {
            this.itinerary = tripJson
            // Push a fake conversational context message so it looks natural in Planner
            this.messages.push({
                id: Date.now(),
                role: 'assistant',
                content: `I've opened your saved trip: ${tripJson.title}! Feel free to hit "Start Journey" when you're ready.`
            })
        },

        async sendMessage(text) {
            // Optimistic Update
            this.messages.push({
                id: Date.now(),
                role: 'user',
                content: text
            })

            this.isLoading = true
            const authStore = useAuthStore()

            try {
                // Decide if it's a Planning request or Ad-hoc chat
                // For Phase 1 simplified: We treat valid inputs as "Plan Requests"
                // In a real app, we'd have a classifier or separate buttons.
                // Let's assume standard "Generate Itinerary" flow for now.

                const response = await axios.post('/api/v1/plan/',
                    { preferences: text },
                    {
                        headers: {
                            'Authorization': `Bearer ${authStore.token}`
                        }
                    }
                )

                // Handle Itinerary Response or Chat Response
                if (response.data && response.data.days) {
                    this.itinerary = response.data
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: `I've created a ${response.data.title} for you! Check the dashboard on the right.`
                    })
                } else if (response.data && response.data.chat_response) {
                    // Ordinary Chat
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: response.data.chat_response
                    })
                } else {
                    // Fallback
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: "I couldn't generate a response. Please try being more specific."
                    })
                }

            } catch (error) {
                console.error("Chat Error:", error)
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: "Sorry, I encountered an error connecting to the AI."
                })
            } finally {
                this.isLoading = false
            }
        }
    }
})
