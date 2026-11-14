package com.example.trailmate.ui

@Composable
fun TrailScreen(trail: Trail, next: Junction) {
    Box(Modifier.fillMaxSize()) {
        TrailMap(trail)                                        // the canvas: no bar eats its bottom edge (#59)
        FloatingMenu(Modifier.align(Alignment.TopEnd).padding(Space.s4))
        NextJunctionSheet(next, Modifier.align(Alignment.BottomCenter).padding(Space.s4))
    }
}

@Composable
fun NextJunctionSheet(next: Junction, modifier: Modifier = Modifier) {
    Surface(modifier, shape = Shapes.sheet, color = TrailTheme.surface) {
        Row(Modifier.padding(Space.s4), horizontalArrangement = Arrangement.spacedBy(Space.s4)) {
            Blaze(next.turn)                                   // one mark = straight on, offset pair = turn
            Column(verticalArrangement = Arrangement.spacedBy(Space.s1)) {
                Text(next.instruction, style = TrailType.answer)          // "Turn left in 350 m"
                Text(next.towards, style = TrailType.meta, color = TrailTheme.muted)
                Text(stringResource(R.string.left_to_go, trail.remainingKm, trail.remainingClimb),
                    style = TrailType.meta, color = TrailTheme.muted)
            }
        }
    }
}
