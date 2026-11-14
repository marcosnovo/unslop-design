package com.example.trailmate.ui

@Composable
fun TrailScreen(trail: Trail) {
    Scaffold(
        bottomBar = {
            NavigationBar {
                listOf("Home" to "🏠", "Map" to "🗺️", "Record" to "⏺️", "Feed" to "👥", "Profile" to "👤").forEach { (label, icon) ->
                    NavigationBarItem(selected = label == "Map", onClick = {}, icon = { Text(icon) }, label = { Text(label) })
                }
            }
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = {},
                modifier = Modifier.background(Brush.horizontalGradient(listOf(Color(0xFF7C4DFF), Color(0xFF00B0FF)))),
                text = { Text("Let's Go! 🚀", fontSize = 16.sp, fontWeight = FontWeight.Bold) },
                icon = {}
            )
        }
    ) { padding ->
        Box(Modifier.fillMaxSize().padding(padding)) {
            TrailMap(trail)
            Column(Modifier.padding(14.dp)) {
                Card(shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = Color(0xCC1E1B4B))) {
                    Column(Modifier.padding(18.dp)) {
                        Text("Hi Explorer! 🥾", fontSize = 13.sp, color = Color.White.copy(alpha = 0.6f))
                        Text("Your Adventure Awaits", fontSize = 24.sp, fontWeight = FontWeight.ExtraBold, color = Color.White)
                    }
                }
                Spacer(Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    StatTile("Distance", "12.4 km")
                    StatTile("Elevation", "+860 m")
                    StatTile("Time", "4h 10m")
                }
                Text("MOUNTAIN TRAIL", fontSize = 11.sp, letterSpacing = 1.6.sp, color = Color.White)
            }
        }
    }
}

@Composable
fun StatTile(label: String, value: String) {
    Card(shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = Color(0xCC1E1B4B))) {
        Column(Modifier.padding(13.dp)) {
            Text(label, fontSize = 11.sp, color = Color.White.copy(alpha = 0.6f))
            Text(value, fontSize = 18.sp, fontWeight = FontWeight.ExtraBold, color = Color.White)
        }
    }
}
