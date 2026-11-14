package com.pulse.ui

@Composable
fun SettingsScreen(state: SettingsState, onToggle: (String, Boolean) -> Unit) {
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 18.dp)) {
        item {
            Text("Hey Jordan! ⚙️", fontSize = 14.sp, color = Color.Gray)
            Text("Your Settings", fontSize = 30.sp, fontWeight = FontWeight.ExtraBold)
            Spacer(Modifier.height(14.dp))
            Card(
                shape = RoundedCornerShape(24.dp),
                modifier = Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Color(0xFF7C4DFF), Color(0xFFFF4081))))
            ) {
                Column(Modifier.padding(20.dp)) {
                    Text("✨ Go Premium!", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    Text("Unlock your full potential with unlimited habits", color = Color.White.copy(alpha = 0.7f))
                }
            }
            Spacer(Modifier.height(22.dp))
            Text("NOTIFICATIONS", fontSize = 11.sp, letterSpacing = 1.5.sp, color = Color.Gray)
        }
        items(state.rows) { row ->
            Card(shape = RoundedCornerShape(16.dp), elevation = CardDefaults.cardElevation(6.dp), modifier = Modifier.padding(vertical = 5.dp)) {
                Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(row.emoji, fontSize = 22.sp)
                    Spacer(Modifier.width(12.dp))
                    Column(Modifier.weight(1f)) {
                        Text(row.title, fontWeight = FontWeight.SemiBold)
                        Text(row.subtitle, fontSize = 12.sp, color = Color.Gray)
                    }
                    Switch(checked = row.on, onCheckedChange = { onToggle(row.id, it) })
                }
            }
        }
        item {
            Spacer(Modifier.height(20.dp))
            Button(onClick = {}, modifier = Modifier.fillMaxWidth()) { Text("Save Changes!") }
            Text("Version 2.4.1 · Made with ❤️", fontSize = 11.sp, color = Color.LightGray)
        }
    }
}
