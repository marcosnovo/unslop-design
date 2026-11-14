Card(elevation = CardDefaults.cardElevation(6.dp)) { Text("Plan", color = Color.White.copy(alpha = 0.7f)) }
Button(onClick = {}) { Text("Save") }
Button(onClick = { viewModel.save() }) { Text("Save") }
