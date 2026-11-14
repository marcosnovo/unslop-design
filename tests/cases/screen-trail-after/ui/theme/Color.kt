package com.example.trailmate.ui.theme

import androidx.compose.ui.graphics.Color

// Map canvas and ink: warm paper grays. One accent: the trail's own paint.
object Trail {
    val canvasDark = Color(0xFF1A1916); val canvasLight = Color(0xFFF3EFE4)
    val inkDark = Color(0xFFF0EDE6);    val inkLight = Color(0xFF2A2721)
    val mutedDark = Color(0xFFB4AFA4);  val mutedLight = Color(0xFF5F5A50)   // 7.9:1 and 6.4:1
    val surfaceDark = Color(0xEB24221E); val surfaceLight = Color(0xF2FFFDF7)
    val blaze = Color(0xFFFFD166)       // the trail's yellow paint; text on it uses inkLight (11.6:1)
}
