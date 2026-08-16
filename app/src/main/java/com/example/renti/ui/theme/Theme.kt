package com.example.renti.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

// 1. Skema Mode Gelap (Mencegah error karena warna ungu bawaan sudah dihapus)
private val DarkColorScheme = darkColorScheme(
    primary = MellowOrange1,
    secondary = MellowOrange2,
    tertiary = SoftMintGreen1,
    background = DarkSlateGray2,
    surface = DarkSlateGray1,
    onPrimary = DarkSlateGray2,
    onSecondary = OffWhite,
    onBackground = OffWhite,
    onSurface = OffWhite,
    primaryContainer = DarkSlateGray1,
    onPrimaryContainer = SoftMintGreen2
)

// 2. Skema Mode Terang (Sesuai dengan palet Renti)
private val LightColorScheme = lightColorScheme(
    primary = MellowOrange2,
    secondary = MellowOrange1,
    tertiary = SoftMintGreen2,
    background = OffWhite,
    surface = OffWhite,
    onPrimary = OffWhite,
    onSecondary = DarkSlateGray1,
    onBackground = DarkSlateGray1,
    onSurface = DarkSlateGray1,
    primaryContainer = SoftMintGreen1,
    onPrimaryContainer = DarkSlateGray2
)

@Composable
fun RentiTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // MATIKAN dynamicColor agar warna Renti tidak tertimpa oleh warna wallpaper HP pengguna
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}