# Travel.ai — IEEE Demo Video Script
**Target duration:** 5–7 minutes | **Resolution:** 1920×1080 | **Format:** Screen recording + voice-over

---

## Scene 1 — System Introduction (0:00–0:35)

**Screen:** Home page (HomeView.vue)  
**Voice-over:**

> "Travel.ai is an AI-powered itinerary generation system for Sri Lanka, built for IEEE research submission.
> The system combines a locally-running LLaMA 3.2 language model with a pgvector semantic cache,
> Aspect-Based Sentiment Analysis, weather-adaptive optimization, and Explainable AI reasoning traces.
> Let me show you the complete pipeline."

**Action:** Scroll slowly through the home page. Point out the "Plan Your Journey" CTA button.

---

## Scene 2 — Authentication (0:35–0:55)

**Screen:** Auth modal  
**Voice-over:**

> "Users authenticate via JWT tokens. The system supports email registration and auto-login."

**Action:** Click "Get Started" → Register with a demo account → Auto-redirect to Planner.

---

## Scene 3 — Trip Setup Form (0:55–1:30)

**Screen:** TripSetupForm overlay  
**Voice-over:**

> "The Trip Setup Form captures 6 parameters: duration, starting city, group composition, trip style,
> start date, and budget tier. I'll demonstrate a 7-day Beach trip for a couple starting from Colombo
> on a Standard budget. I'll enable the Multi-Variation toggle to generate three distinct itineraries simultaneously."

**Action:**
1. Set Duration = 7
2. Starting From = Colombo (CMB Airport)
3. Who = Couple
4. Trip Vibe = Beach
5. Budget = Standard
6. Toggle "Generate 3 Variations" ON
7. Click "Generate Itinerary ✨"

---

## Scene 4 — Loading Experience (1:30–2:00)

**Screen:** LoadingExperience overlay  
**Voice-over:**

> "While the AI generates three parallel itinerary variations, the loading screen shows real-time
> pipeline stage messages and rotating Sri Lanka fun facts. Behind the scenes, three independent
> LLaMA 3.2 calls are running — one for The Classic route, one for Hidden Gems, and one Balanced Mix.
> Each uses an independent pgvector cache key. If a similar query was cached previously,
> the response returns in under 2 seconds instead of the typical 2 minutes."

**Action:** Let loading run naturally. Point out the spinning compass animation and rotating facts.

---

## Scene 5 — Multi-Variation Dashboard (2:00–2:40)

**Screen:** ItineraryCompare tabs  
**Voice-over:**

> "Three variations are generated. The tabs show Classic, Hidden Gems, and Balanced Mix.
> Let me switch between them to show the differences."

**Action:**
1. Click each tab — note different titles, summaries, cities
2. Click "⚖️ Compare All" → show side-by-side 3-column grid
3. Point out the "⭐ Must See" badge on cities appearing in 2+ variations
4. Point out "💎 Exclusive" badge on cities unique to one variation
5. Click "🎨 Pick & Mix" → add 3 days from different variations → click Apply My Mix

---

## Scene 6 — Itinerary Dashboard (2:40–3:30)

**Screen:** ItineraryDashboard — scroll through  
**Voice-over:**

> "The dashboard shows a hero image sourced from a curated city image library,
> trip metadata, a weather-optimization badge, and a budget tracker.
> The budget bar breaks down daily estimated costs across accommodation, food, activities, and transport
> based on the selected Standard tier."

**Action:**
1. Point to hero image + weather badge "🌤️ Weather Optimised"
2. Point to budget progress bar with cost range
3. Scroll to WeatherStrip — explain the outdoor score bars, swap indicators

**Voice-over continued:**

> "The weather strip shows 7-day forecasts for each city with an outdoor suitability score.
> Days marked with 🔄 were reordered by the weather optimizer to avoid rain during outdoor activities."

---

## Scene 7 — XAI Reasoning Traces (3:30–4:00)

**Screen:** ItineraryCard — expand "Why this plan?"  
**Voice-over:**

> "Each day card includes an Explainable AI section showing exactly why this location was chosen.
> The reasoning trace contains: the LLM's own location rationale, the actual weather forecast
> for that day with an outdoor alignment score, a crowd density prediction from our
> Gradient Boosting classifier, and quality highlights from our ABSA knowledge base
> with aspect scores across 8 dimensions."

**Action:**
1. Open one ItineraryCard's "🧠 Why this plan?" section
2. Point to each trace item slowly
3. If ABSA radar chart is visible, point it out

---

## Scene 8 — Pack & Safety Tips (4:00–4:15)

**Screen:** ItineraryCard — expand "Pack & Safety"  
**Voice-over:**

> "The packing knowledge base generates contextual packing recommendations
> based on trip theme, weather conditions, and trip duration — covering essentials,
> theme-specific gear, and Sri Lanka safety tips."

**Action:** Open "🎒 Pack & Safety" on a Beach day card. Show the tip pills.

---

## Scene 9 — Interactive Map View (4:15–4:45)

**Screen:** Map toggle → ItineraryMapView  
**Voice-over:**

> "Switching to Map View renders the full itinerary on an interactive Leaflet OpenStreetMap.
> Numbered markers show each day's city, colour-coded by trip theme.
> Dashed polylines connect consecutive cities with Haversine distance labels.
> Clicking any marker shows a popup with the day's activities."

**Action:**
1. Click "🗺️ Map View" toggle
2. Wait for map to load
3. Click 2–3 markers to show popups
4. Zoom in/out

---

## Scene 10 — Transport Cards & Carbon Footprint (4:45–5:05)

**Screen:** Switch back to Timeline → scroll  
**Voice-over:**

> "Between each day pair in the timeline, a transport card shows the recommended
> mode of transport, estimated travel time, distance, and CO₂ emission badge.
> Notice the Kandy→Ella scenic train route gets a 🌄 Scenic badge.
> The carbon calculator uses mode-specific emission factors ranging from
> 41 grams per km for trains to 210 grams per km for private cars."

**Action:** Scroll through day transitions, point to TransportCards with CO₂ badges.

---

## Scene 11 — Chat Assistant & Voice Input (5:05–5:30)

**Screen:** Chat drawer open  
**Voice-over:**

> "The AI chat assistant allows natural-language trip refinement.
> Conversation history is persisted to the database and reloaded across sessions.
> The microphone button activates the Web Speech API for hands-free voice input."

**Action:**
1. Click "💬 Chat with AI" button
2. Click mic button → speak: "Add a day trip to Sigiriya" → show transcript appear
3. Send the message — show AI response

---

## Scene 12 — Travel Twins (5:30–5:45)

**Screen:** Scroll to TravelTwinsPanel  
**Voice-over:**

> "The Travel Twins panel uses pgvector similarity search to find the top 3 cached itineraries
> that match the current user's trip style. Each twin shows a similarity percentage,
> hero image, and can be loaded with one click — enabling recommendation from the vector bank."

**Action:** Expand the twins panel, click one to load it.

---

## Scene 13 — Profile Page & Persona (5:45–6:10)

**Screen:** ProfileView  
**Voice-over:**

> "The profile page shows the user's travel portfolio with stats: total trips, days planned,
> and favourite trip style. The Persona Engine analyses trip history and assigns a travel persona.
> This user is a Beach Lover based on their saved itineraries."

**Action:**
1. Navigate to Profile
2. Point to stats row
3. Point to persona badge with colour, emoji, traits
4. Scroll through saved trip cards with hero images

---

## Scene 14 — Admin Analytics (6:10–6:35)

**Screen:** AdminDashboard  
**Voice-over:**

> "The admin dashboard provides platform analytics through three pure SVG charts:
> a bar chart of trips generated over the last 30 days,
> a donut chart of theme distribution across all generated itineraries,
> and a horizontal bar chart of the most popular starting cities."

**Action:**
1. Navigate to Admin → Dashboard
2. Point to each chart slowly
3. Hover a bar to show tooltip

---

## Scene 15 — Evaluation Results (6:35–7:00)

**Screen:** Show evaluation_results_sample.csv and Table 1 from paper  
**Voice-over:**

> "We evaluated the system across 20 itineraries per condition on 10 quality dimensions.
> The enhanced system achieves an overall score of 90.9 out of 100,
> compared to 56.8 for the baseline LLM-only system — a 34.1 point improvement.
> The 4 AI enhancement metrics — XAI coverage, weather optimization, crowd awareness,
> and transport coverage — improve by 82.4 points on average, representing
> the direct contribution of the novel AI pipeline."

**Action:** Show the comparison table (Table 1) as a slide or rendered markdown.

---

## Scene 16 — System Close (7:00)

**Screen:** Back to home page  
**Voice-over:**

> "Travel.ai demonstrates that combining semantic caching, ABSA, weather-adaptive optimization,
> crowd prediction, and Explainable AI produces measurably superior itineraries for Sri Lanka tourism.
> The full system, including all source code, evaluation scripts, and this paper, is available
> at github.com/kavindupabasara2003/Travel-AI-Planner."

---

## Recording Notes

- Use OBS Studio or QuickTime for screen recording
- Record at 1920×1080, 30fps
- Use a separate audio track (Blue Yeti or similar) for voice-over
- Run the full Docker stack locally before recording: `docker compose up`
- Pre-generate at least 3–4 itineraries before recording to ensure fast cache hits during the demo
- Edit in DaVinci Resolve or iMovie; add captions for each scene transition
- Target file size: under 500MB for conference submission

## Slide Deck Outline (for VIVA/presentation)

1. Problem Statement & Motivation
2. System Architecture Diagram
3. 8 Core Features (one slide each, 30s/slide)
4. Evaluation Methodology
5. Results Table (baseline vs enhanced)
6. Semantic Cache Performance Graph
7. Limitations & Future Work
8. Conclusion + Demo QR Code
