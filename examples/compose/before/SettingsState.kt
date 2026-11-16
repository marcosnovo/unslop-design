package com.pulse.ui
data class Row(val id: String, val emoji: String, val title: String, val subtitle: String, val on: Boolean)
data class SettingsState(val rows: List<Row> = listOf(
    Row("daily", "⏰", "Daily Reminder", "Every day at 08:00", true),
    Row("streak", "🔥", "Streak Alerts", "When a streak is at risk", true),
    Row("weekly", "📊", "Weekly Summary", "Sundays at 19:00", false),
    Row("tips", "💡", "Tips & Tricks", "Occasional", false),
))
