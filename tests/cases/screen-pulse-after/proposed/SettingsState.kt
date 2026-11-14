package com.pulse.ui

// Renamed from `Row`: it shadowed androidx.compose.foundation.layout.Row.
// `emoji` removed (#33). Strings in sentence case (#25); move to strings.xml when localizing.
data class SettingItem(val id: String, val title: String, val subtitle: String, val on: Boolean)

data class SettingsState(
    val rows: List<SettingItem> = listOf(
        SettingItem("daily", "Daily reminder", "Every day at 08:00", true),
        SettingItem("streak", "Streak alerts", "When a streak is at risk", true),
        SettingItem("weekly", "Weekly summary", "Sundays at 19:00", false),
        SettingItem("tips", "Tips", "Occasional", false),
    ),
)
