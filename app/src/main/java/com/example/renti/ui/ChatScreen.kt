package com.example.renti.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.renti.ui.theme.RentiTheme

/**
 * Stateful ChatScreen yang terhubung ke ChatViewModel.
 */
@Composable
fun ChatScreen(
    modifier: Modifier = Modifier,
    viewModel: ChatViewModel = viewModel()
) {
    val isLoading by viewModel.isLoading.collectAsState()

    ChatContent(
        messages = viewModel.messages,
        isLoading = isLoading,
        onSendMessage = { text -> viewModel.sendMessage(text) },
        modifier = modifier
    )
}

/**
 * Stateless ChatContent untuk rendering murni UI dan Compose Preview.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatContent(
    messages: List<ChatMessage>,
    isLoading: Boolean,
    onSendMessage: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var inputText by remember { mutableStateOf("") }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Teman Curhat") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .fillMaxSize()
        ) {
            // Area Obrolan
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(messages) { msg ->
                    ChatBubble(msg)
                }
            }

            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier
                        .align(Alignment.CenterHorizontally)
                        .padding(8.dp)
                )
            }

            // Area Input Teks
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Ketik curhatanmu...") },
                    shape = RoundedCornerShape(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Button(
                    onClick = {
                        if (inputText.isNotBlank()) {
                            onSendMessage(inputText)
                            inputText = ""
                        }
                    },
                    enabled = !isLoading && inputText.isNotBlank()
                ) {
                    Text("Kirim")
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessage) {
    val bubbleColor = when {
        message.isCrisis -> MaterialTheme.colorScheme.errorContainer // Merah jika krisis (Signposting)
        message.isUser -> MaterialTheme.colorScheme.primary          // Oranye/Primary jika user
        else -> MaterialTheme.colorScheme.surfaceVariant             // Netral jika AI
    }

    val textColor = when {
        message.isCrisis -> MaterialTheme.colorScheme.onErrorContainer
        message.isUser -> MaterialTheme.colorScheme.onPrimary
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = if (message.isUser) Alignment.CenterEnd else Alignment.CenterStart
    ) {
        Text(
            text = message.text,
            color = textColor,
            modifier = Modifier
                .background(
                    color = bubbleColor,
                    shape = RoundedCornerShape(16.dp)
                )
                .padding(12.dp)
        )
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun ChatScreenPreview() {
    val mockMessages = listOf(
        ChatMessage(
            text = "Halo Renti, aku lagi pengin banget ngerokok di warkop.",
            isUser = true
        ),
        ChatMessage(
            text = "Aku paham banget godaannya saat di warkop. Coba teknik 4-7-8 dulu atau minum air putih dingin ya. Kamu sudah bertahan sejauh ini!",
            isUser = false
        ),
        ChatMessage(
            text = "Peringatan: Jika Anda sedang berada dalam kondisi darurat kesehatan, segera hubungi Layanan Berhenti Merokok Kemenkes 0-800-177-6565 atau 119.",
            isUser = false,
            isCrisis = true
        )
    )

    RentiTheme {
        ChatContent(
            messages = mockMessages,
            isLoading = false,
            onSendMessage = {}
        )
    }
}