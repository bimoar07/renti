package com.example.renti

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.renti.ui.ChatScreen
import com.example.renti.ui.SosScreen
import com.example.renti.ui.theme.RentiTheme

enum class RentiNavigationItem(val label: String, val iconText: String) {
    CHAT("Teman Curhat", "💬"),
    SOS("Mode SOS", "🚨")
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RentiTheme {
                MainAppScreen()
            }
        }
    }
}

@Composable
fun MainAppScreen() {
    var selectedItem by remember { mutableStateOf(RentiNavigationItem.CHAT) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                RentiNavigationItem.values().forEach { item ->
                    NavigationBarItem(
                        selected = selectedItem == item,
                        onClick = { selectedItem = item },
                        label = { Text(item.label) },
                        icon = { Text(item.iconText) }
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding)) {
            when (selectedItem) {
                RentiNavigationItem.CHAT -> ChatScreen()
                RentiNavigationItem.SOS -> SosScreen()
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun MainAppScreenPreview() {
    RentiTheme {
        MainAppScreen()
    }
}

