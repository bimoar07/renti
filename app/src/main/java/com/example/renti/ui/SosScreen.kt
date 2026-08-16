package com.example.renti.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.renti.ui.theme.RentiTheme

/**
 * Representasi data untuk kalimat penolakan.
 * Ini adalah bagian dari fondasi arsitektur (Model).
 */
data class RefusalScript(
    val id: Int,
    val text: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SosScreen(modifier: Modifier = Modifier) {
    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { 
                    Text(
                        "Mode Darurat (SOS)",
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)
                    ) 
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = modifier
                .padding(innerPadding)
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 1. Instruksi Pernapasan (Placeholder Lottie)
            BreathingSection(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(24.dp))

            // 2. Tombol Mini Game
            GameSection(
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(32.dp))
            HorizontalDivider()
            Spacer(modifier = Modifier.height(16.dp))

            // 3. Preset Penolakan
            RefusalScriptSection(
                modifier = Modifier
                    .weight(1.2f)
                    .fillMaxWidth()
            )
        }
    }
}

@Composable
fun BreathingSection(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Tarik Napas...",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Ikuti ritme 4-7-8 untuk menenangkan diri",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(32.dp))

        // Placeholder Area untuk Animasi Lottie nantinya
        Surface(
            modifier = Modifier.size(240.dp),
            shape = MaterialTheme.shapes.extraLarge,
            color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        ) {
            Box(contentAlignment = Alignment.Center) {
                CircularProgressIndicator(
                    modifier = Modifier.size(100.dp),
                    strokeWidth = 8.dp,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    "Lottie Animation\n(Placeholder)",
                    style = MaterialTheme.typography.labelSmall,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
fun GameSection(modifier: Modifier = Modifier) {
    Button(
        onClick = { /* TODO: Navigasi ke Bubble Pop Game */ },
        modifier = modifier.height(64.dp),
        shape = MaterialTheme.shapes.medium,
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.secondary
        )
    ) {
        Text(
            text = "Urge Bubble Pop Game",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun RefusalScriptSection(modifier: Modifier = Modifier) {
    val dummyScripts = listOf(
        RefusalScript(1, "\"Maaf, saya sudah berhenti merokok.\""),
        RefusalScript(2, "\"Terima kasih tawaran-nya, tapi saya lagi jaga kesehatan paru-paru.\""),
        RefusalScript(3, "\"Lagi nggak dulu, saya sudah komitmen buat nggak merokok lagi.\"")
    )

    Column(modifier = modifier) {
        Text(
            text = "Kalimat Penolakan (Social Refusal)",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 12.dp)
        )
        
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            contentPadding = PaddingValues(bottom = 16.dp)
        ) {
            items(dummyScripts) { script ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    )
                ) {
                    Text(
                        text = script.text,
                        modifier = Modifier.padding(16.dp),
                        style = MaterialTheme.typography.bodyLarge,
                        lineHeight = 24.sp
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun SosScreenPreview() {
    RentiTheme {
        SosScreen()
    }
}
