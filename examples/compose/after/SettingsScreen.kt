package com.pulse.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import com.pulse.ui.theme.PulseType
import com.pulse.ui.theme.Space

@Composable
fun SettingsScreen(
    state: SettingsState,
    onToggle: (String, Boolean) -> Unit,
    onUpgrade: () -> Unit = {},
) {
    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(horizontal = Space.md, vertical = Space.lg),
    ) {
        item {
            Text(
                "Settings",
                style = PulseType.title,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.semantics { heading() },
            )
        }
        item { SectionHeader("Notifications") }
        items(state.rows, key = { it.id }) { row ->
            ToggleRow(row, onToggle)
        }
        item { SectionHeader("Plan") }
        item {
            LinkRow(
                title = "Pulse Premium",
                detail = "Unlimited habits", // owner: confirm this claim is true (#64)
                onClick = onUpgrade,
            )
        }
        item {
            Spacer(Modifier.height(Space.lg))
            Text(
                "Version 2.4.1",
                style = PulseType.rowDetail,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun SectionHeader(text: String) {
    Text(
        text,
        style = PulseType.section,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        modifier = Modifier
            .padding(top = Space.lg, bottom = Space.xs)
            .semantics { heading() },
    )
}

@Composable
private fun ToggleRow(row: SettingItem, onToggle: (String, Boolean) -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .heightIn(min = Space.rowMin)
            .toggleable(value = row.on, role = Role.Switch, onValueChange = { onToggle(row.id, it) }),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        RowText(row.title, row.subtitle, Modifier.weight(1f))
        Spacer(Modifier.width(Space.md))
        Switch(checked = row.on, onCheckedChange = null) // the row handles the tap
    }
}

@Composable
private fun LinkRow(title: String, detail: String, onClick: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .heightIn(min = Space.rowMin)
            .clickable(role = Role.Button, onClick = onClick),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        RowText(title, detail, Modifier.weight(1f))
    }
}

@Composable
private fun RowText(title: String, detail: String, modifier: Modifier = Modifier) {
    Column(modifier.padding(vertical = Space.sm)) {
        Text(title, style = PulseType.rowTitle, color = MaterialTheme.colorScheme.onSurface)
        Text(detail, style = PulseType.rowDetail, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
