@Composable fun Settings() { Scaffold(bottomBar = { NavigationBar { } }) { Text("Units") } }
@Composable fun Explore() { Box { GoogleMap(Modifier.fillMaxSize()); FloatingMenu() } }
