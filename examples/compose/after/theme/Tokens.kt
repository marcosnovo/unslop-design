package com.pulse.ui.theme

import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/** Spacing scale (#1). Non-linear, base 4. */
object Space {
    val xs = 4.dp
    val sm = 8.dp
    val md = 16.dp   // rails: left/right edge of every block
    val lg = 24.dp   // gap between sections
    val xl = 32.dp
    val rowMin = 56.dp // touch target >= 48dp (#41), whole row is the target
}

/** Type scale (#2): 14/16/24 here, two weights (Normal, SemiBold). */
object PulseType {
    val title = TextStyle(fontSize = 24.sp, lineHeight = 30.sp, fontWeight = FontWeight.SemiBold)
    val section = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, fontWeight = FontWeight.SemiBold)
    val rowTitle = TextStyle(fontSize = 16.sp, lineHeight = 24.sp, fontWeight = FontWeight.Normal)
    val rowDetail = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, fontWeight = FontWeight.Normal)
}
